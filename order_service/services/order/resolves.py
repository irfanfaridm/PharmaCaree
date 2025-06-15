import graphene
import requests
from datetime import datetime
from database import db_session, Order

class OrderType(graphene.ObjectType):
    id = graphene.Int()
    userId = graphene.Int(source='user_id')
    drugId = graphene.Int(source='drug_id')
    drugName = graphene.String(source='drug_name')
    quantity = graphene.Int()
    totalPrice = graphene.Float(source='total_price')
    orderDate = graphene.DateTime(source='order_date')

class CreateOrder(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        drug_id = graphene.Int(required=True)
        drug_name = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        total_price = graphene.Float(required=True)

    Output = OrderType

    def mutate(self, info, user_id, drug_id, drug_name, quantity, total_price):
        order = Order(
            user_id=user_id,
            drug_id=drug_id,
            drug_name=drug_name,
            quantity=quantity,
            total_price=total_price
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        # Logic to call Payment Service
        payment_service_url = "http://payment-service:5003/graphql"
        payment_status = "pending" # Initial status for the payment
        payment_date = order.order_date.isoformat() # Use the order date

        create_payment_mutation = f"""
            mutation {{
                createPayment(
                    customer: {user_id},
                    amount: {total_price},
                    status: \"{payment_status}\",
                    date: \"{payment_date}\"
                ) {{
                    id
                    customer
                    amount
                    status
                    date
                }}
            }}
        """
        print(f"[order_service] Mengirim mutasi createPayment ke payment_service: {create_payment_mutation}")

        try:
            payment_response = requests.post(payment_service_url, json={'query': create_payment_mutation})
            print(f"[order_service] Respons status code dari payment_service: {payment_response.status_code}")
            print(f"[order_service] Respons text dari payment_service: {payment_response.text}")
            payment_result = payment_response.json()
            print(f"[order_service] Menerima respons JSON dari payment_service: {payment_result}")

            if payment_result.get("errors"):
                print(f"[order_service] GraphQL Payment Errors dari payment_service: {payment_result['errors']}")
                # TODO: Implement rollback logic for order if payment creation fails
        except Exception as e:
            print(f"[order_service] Kesalahan saat memanggil Payment Service: {e}")
            # TODO: Implement rollback logic for order if payment service call fails

        return order

class TrackOrderAndCreateDelivery(graphene.Mutation):
    class Arguments:
        order_id = graphene.Int(required=True)

    Output = graphene.String

    def mutate(self, info, order_id):
        order = db_session.query(Order).filter(Order.id == order_id).first()
        if not order:
            return "Order not found."

        # Query Payment Service to check payment status
        payment_service_url = "http://payment-service:5003/graphql"
        get_payments_query = """
            query {
                allPayments {
                    id
                    customer
                    amount
                    status
                }
            }
        """
        try:
            payment_response = requests.post(payment_service_url, json={'query': get_payments_query})
            payment_result = payment_response.json()

            if payment_result.get("errors"):
                return f"Error querying payment service: {payment_result['errors']}"

            payments = payment_result['data']['allPayments']
            paid_payment = next((p for p in payments if p['customer'] == order.user_id and p['amount'] == order.total_price and p['status'] == 'paid'), None)

            if not paid_payment:
                return "Order not yet paid or payment not found."

            # If paid, call Delivery Service
            delivery_service_url = "http://delivery-service:5004/graphql"
            # Placeholder address - You might want to get this from a user service or order details if available
            delivery_address = "User's Registered Address" 
            
            create_delivery_mutation = f"""
                mutation {{
                    createDelivery(
                        orderId: \"{order.id}\",
                        address: \"{delivery_address}\",
                        status: \"pending\"
                    ) {{
                        orderId
                        status
                    }}
                }}
            """
            print(f"[order_service] Sending createDelivery mutation to delivery_service: {create_delivery_mutation}")

            delivery_response = requests.post(delivery_service_url, json={'query': create_delivery_mutation})
            delivery_result = delivery_response.json()

            print(f"[order_service] Received JSON response from delivery_service: {delivery_result}")

            if delivery_result.get("errors"):
                return f"Error creating delivery: {delivery_result['errors']}"

            return f"Delivery initiated for order {order_id}. Status: {delivery_result['data']['createDelivery']['status']}"

        except Exception as e:
            return f"Error connecting to service: {e}"

class OrderResolves(graphene.ObjectType):
    all_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.Int())

    def resolve_all_orders(self, info):
        return db_session.query(Order).all()

    def resolve_order(self, info, id):
        return db_session.query(Order).filter(Order.id == id).first()

    create_order = CreateOrder.Field()
    track_order_and_create_delivery = TrackOrderAndCreateDelivery.Field() 