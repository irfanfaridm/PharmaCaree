import requests
from ariadne import QueryType, MutationType, ObjectType
from database import get_all_drugs, get_drug_by_id, create_drug, update_drug, delete_drug, decrement_drug_stock_atomically, increment_drug_stock

drug_query = QueryType()
drug_mutation = MutationType()

# Define the Order type resolver to ensure it can be returned
# This is a representation of the Order type from the order-service schema
# It's defined here so processAddToCart can return an Order object
order_type = ObjectType("Order")

@order_type.field("id")
def resolve_order_id(obj, info):
    return str(obj.get("id"))

@order_type.field("userId")
def resolve_order_user_id(obj, info):
    return obj.get("userId")

@order_type.field("drugId")
def resolve_order_drug_id(obj, info):
    return obj.get("drugId")

@order_type.field("drugName")
def resolve_order_drug_name(obj, info):
    return obj.get("drugName")

@order_type.field("quantity")
def resolve_order_quantity(obj, info):
    return obj.get("quantity")

@order_type.field("totalPrice")
def resolve_order_total_price(obj, info):
    return obj.get("totalPrice")

@order_type.field("status")
def resolve_order_status(obj, info):
    return obj.get("status")

@order_type.field("orderDate")
def resolve_order_created_at(obj, info):
    return obj.get("orderDate")

@drug_query.field("drugs")
def resolve_drugs(_, info, query=None, category=None):
    return get_all_drugs(query, category)

@drug_query.field("drugById")
def resolve_drug_by_id(_, info, id):
    return get_drug_by_id(id)

@drug_mutation.field("createDrug")
def resolve_create_drug(_, info, name, description, price, stock, category):
    new_drug = create_drug(name, description, price, stock, category)
    return new_drug if new_drug else None

@drug_mutation.field("updateDrug")
def resolve_update_drug(_, info, id, name=None, description=None, price=None, stock=None, category=None):
    success = update_drug(id, name, description, price, stock, category)
    # After updating, fetch and return the updated drug if needed for a more complete response
    return get_drug_by_id(id) if success else None

@drug_mutation.field("deleteDrug")
def resolve_delete_drug(_, info, id):
    success = delete_drug(id)
    return success

@drug_mutation.field("processAddToCart")
def resolve_process_add_to_cart(_, info, drugId, quantity, userId):
    try:
        drug = get_drug_by_id(drugId)
        if not drug:
            return {"success": False, "message": "Obat tidak ditemukan.", "order": None, "drug": None}

        if drug["stock"] < quantity:
            return {"success": False, "message": "Stok tidak mencukupi.", "order": None, "drug": None}

        # 1. Decrement stock locally (atomically)
        # Note: We pass original drugId to decrement_drug_stock_atomically
        stock_decremented = decrement_drug_stock_atomically(drugId, quantity)
        if not stock_decremented:
            return {"success": False, "message": "Gagal memperbarui stok obat.", "order": None, "drug": None}

        # 2. Create Order in Order Service
        # Ensure we use the correct service name (from docker-compose.yml)
        order_service_url = "http://order-service:5002/graphql"
        total_price = drug["price"] * quantity
        create_order_mutation = f"""
            mutation {{
                createOrder(
                    userId: {userId},
                    drugId: {drugId},
                    drugName: \"{drug["name"]}\",
                    quantity: {quantity},
                    totalPrice: {total_price}
                ) {{
                    id
                    userId
                    drugId
                    drugName
                    quantity
                    totalPrice
                    orderDate
                }}
            }}
        """
        print(f"[drug_service] Mengirim mutasi createOrder ke order_service: {create_order_mutation}")

        order_response = requests.post(order_service_url, json={'query': create_order_mutation})
        order_result = order_response.json()
        print(f"[drug_service] Menerima respons dari order_service: {order_result}")

        if order_result.get("errors"):
            print(f"[drug_service] GraphQL Order Errors dari order_service: {order_result['errors']}")
            # Rollback stock if order creation failed
            increment_drug_stock(drugId, quantity)
            return {"success": False, "message": f"Gagal membuat pesanan: {order_result['errors'][0]['message']}", "order": None, "drug": None}

        created_order = order_result["data"]["createOrder"]
        print(f"[drug_service] created_order dari order_service: {created_order}")

        # 3. Get updated drug info to return
        updated_drug = get_drug_by_id(drugId)

        return {"success": True, "message": "Pesanan berhasil dibuat dan stok diperbarui.", "order": created_order, "drug": updated_drug}

    except Exception as e:
        print(f"[drug_service] Kesalahan saat memproses tambah ke keranjang: {e}")
        # Ensure stock is rolled back if any other error occurs after decrementing
        # Check if stock_decremented was set to True before attempting rollback
        if 'stock_decremented' in locals() and stock_decremented:
            increment_drug_stock(drugId, quantity)
        return {"success": False, "message": f"Terjadi kesalahan server: {e}", "order": None, "drug": None}

# Combine the resolvers to be used in the schema
drug_resolvers = [drug_query, drug_mutation, order_type] 