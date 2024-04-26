from rest_framework.serializers import ModelSerializer
from searchAPIs.models import ProviderProgressNote
from paymentAPIs.models import Transaction

class ProviderPrgressNoteSerailizer(ModelSerializer):
    class Meta:
        model = ProviderProgressNote
        fields = ['id','consultantiontId','treatmentGoal','subjective','objective','assessment','plan','signatureUrl','createdAt']
    def create(self, validated_data):
        progress = ProviderProgressNote.objects.create(
        consultantiontId=validated_data["consultantiontId"],
        treatmentGoal=validated_data["treatmentGoal"],
        subjective=validated_data["subjective"],
        objective=validated_data["objective"],
        assessment=validated_data["assessment"],
        plan=validated_data["plan"],
        signatureUrl= validated_data["signatureUrl"]
        )
        return progress

class TransactionCreateSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id','consultantiontId','paymentId','userId','amount','paymentMethodId','paymentStatus','callDuration','stripeFee','netAmmount']
    def create(self, validated_data):
        tarnsaction = Transaction.objects.create(
        consultantiontId=validated_data["consultantiontId"],
        paymentId = validated_data["paymentId"],
        userId=validated_data["userId"],
        amount=validated_data["amount"],
        paymentMethodId=validated_data["paymentMethodId"],
        paymentStatus=validated_data["paymentStatus"],
        callDuration=validated_data["callDuration"],
        stripeFee=validated_data["stripeFee"],
        netAmmount=validated_data["netAmmount"]
        )
        return tarnsaction
