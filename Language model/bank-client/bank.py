from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        ls_prediction_endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
        ls_prediction_key = os.getenv('LS_CONVERSATIONS_KEY')

        # Create a client for the Language service model once (OUTSIDE the loop)
        client = ConversationAnalysisClient(ls_prediction_endpoint, AzureKeyCredential(ls_prediction_key))

        # Get user input (until they enter "quit")
        userText = ''
        while userText.lower() != 'quit':
            userText = input('\nEnter some text ("quit" to stop)\n').strip()
            if userText.lower() != 'quit':

                # Call the Language service model to get intent and entities
                cls_project = 'Bank'
                deployment_slot = 'production'

                query = userText
                result = client.analyze_conversation(
                    task={
                        "kind": "Conversation",
                        "analysisInput": {
                            "conversationItem": {
                                "participantId": "1",
                                "id": "1",
                                "modality": "text",
                                "language": "en",
                                "text": query
                            },
                            "isLoggingEnabled": False
                        },
                        "parameters": {
                            "projectName": cls_project,
                            "deploymentName": deployment_slot,
                            "verbose": True
                        }
                    }
                )

                top_intent = result["result"]["prediction"]["topIntent"]
                entities = result["result"]["prediction"]["entities"]

                print("View top intent:")
                print(f"\tTop intent: {top_intent}")
                print(f"\tConfidence score: {result['result']['prediction']['intents'][0]['confidenceScore']}\n")

                print("View entities:")
                for entity in entities:
                    print(f"\tCategory: {entity['category']}")
                    print(f"\tText: {entity['text']}")
                    print(f"\tConfidence score: {entity['confidenceScore']}")

                # Apply the appropriate action
                if top_intent == 'CheckBalance':
                    account_type = next((e["text"] for e in entities if e["category"].lower() == "accounttype"), None)
                    if account_type:
                        print(get_balance(account_type))
                    else:
                        print("Please specify the account type.")

                elif top_intent == 'TransferMoney':
                    amount = next((e["text"] for e in entities if e["category"].lower() == "amount"), None)
                    from_account = None
                    to_account = None
                    for entity in entities:
                        if entity["category"].lower() == "accounttype":
                            if not from_account:
                                from_account = entity["text"]
                            else:
                                to_account = entity["text"]
                    if amount and from_account and to_account:
                        print(transfer_money(amount, from_account, to_account))
                    else:
                        print("Please provide the correct details to transfer money.")

                elif top_intent == 'TrackSpending':
                    category = next((e["text"] for e in entities if e["category"].lower() == "category"), None)
                    time_frame = next((e["text"] for e in entities if e["category"].lower() == "timeframe"), None)
                    if category and time_frame:
                        print(track_spending(category, time_frame))
                    else:
                        print("Please provide a valid category and time frame.")

                elif top_intent == 'PayBill':
                    payee = next((e["text"] for e in entities if e["category"].lower() == "payee"), None)
                    amount = next((e["text"] for e in entities if e["category"].lower() == "amount"), None)
                    time_frame = next((e["text"] for e in entities if e["category"].lower() == "timeframe"), None)
                    if payee and amount and time_frame:
                        print(pay_bill(amount, payee, time_frame))
                    else:
                        print("Please provide both the payee and amount.")

                elif top_intent == 'ReportFraud':
                    amount = next((e["text"] for e in entities if e["category"].lower() == "amount"), None)
                    category = next((e["text"] for e in entities if e["category"].lower() == "category"), None)
                    if amount and category:
                        print(report_fraud(amount, category))
                    else:
                        print("Please specify the fraudulent amount.")

                else:
                    print(f"Sorry, I didn’t understand '{query}'. Try asking about your balance, transactions, or payments.")

    except Exception as ex:
        print(f"Error: {ex}")

# Define helper functions
def get_balance(account_type):
    return f"Your {account_type} account balance is $1,234.56."

def transfer_money(amount, from_account, to_account):
    return f"Transferring ${amount} from {from_account} to {to_account}."

def track_spending(category, time_frame):
    return f"You spent $150 on {category} {time_frame}."

def pay_bill(amount, payee, time_frame):
    return f"Paying ${amount} to {payee} {time_frame or ''}."

def report_fraud(amount, category):
    return f"Reporting a suspicious charge of ${amount} on {category or 'unknown category'}."

if __name__ == "__main__":
    main()
