import graphene
from datetime import datetime

# Sample data (in-memory database)
deliveries = []

class Delivery(graphene.ObjectType):
    orderId = graphene.String()
    address = graphene.String()
    status = graphene.String()
    shippedAt = graphene.String()
    deliveredAt = graphene.String()

class Query(graphene.ObjectType):
    deliveries = graphene.List(Delivery)
    delivery = graphene.Field(Delivery, orderId=graphene.String())

    def resolve_deliveries(self, info):
        return deliveries

    def resolve_delivery(self, info, orderId):
        for delivery in deliveries:
            if delivery["order_id"] == orderId:
                return delivery
        return None

class CreateDelivery(graphene.Mutation):
    class Arguments:
        orderId = graphene.String(required=True)
        address = graphene.String(required=True)
        status = graphene.String(required=True)

    Output = Delivery

    def mutate(self, info, orderId, address, status):
        new_delivery = {
            "orderId": orderId,
            "address": address,
            "status": status,
            "shippedAt": datetime.now().isoformat(),
            "deliveredAt": None # Awalnya null, akan diperbarui nanti
        }
        deliveries.append(new_delivery)
        return Delivery(**new_delivery)

class Mutation(graphene.ObjectType):
    createDelivery = CreateDelivery.Field()

schema = graphene.Schema(query=Query, mutation=Mutation) 