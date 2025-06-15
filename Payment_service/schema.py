import graphene
from models import payments, Payment
from database import add_payment, get_all_payments, update_payment_status

class PaymentType(graphene.ObjectType):
    id = graphene.Int()
    customer = graphene.Int()
    amount = graphene.Float()
    status = graphene.String()
    date = graphene.String()

class Query(graphene.ObjectType):
    all_payments = graphene.List(PaymentType)

    def resolve_all_payments(self, info):
        return get_all_payments()

class CreatePayment(graphene.Mutation):
    class Arguments:
        customer = graphene.Int()
        amount = graphene.Float()
        status = graphene.String()
        date = graphene.String()

    payment = graphene.Field(lambda: PaymentType)

    def mutate(self, info, customer, amount, status, date):
        payment_id = add_payment(customer, amount, status, date)
        return CreatePayment(payment={
            'id': payment_id,
            'customer': customer,
            'amount': amount,
            'status': status,
            'date': date
        })

class UpdatePaymentStatus(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        status = graphene.String()

    payment = graphene.Field(lambda: PaymentType)

    def mutate(self, info, id, status):
        update_payment_status(id, status)
        # Ambil payment yang sudah diupdate
        payment = next((p for p in get_all_payments() if p['id'] == id), None)
        return UpdatePaymentStatus(payment=payment)

class Mutation(graphene.ObjectType):
    createPayment = CreatePayment.Field()
    updatePaymentStatus = UpdatePaymentStatus.Field()

schema = graphene.Schema(query=Query, mutation=Mutation) 