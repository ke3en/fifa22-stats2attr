from pathlib import Path

from firebase_admin import credentials, firestore, initialize_app

from stats2attr import get_player_attr, get_player_ovr

CRED_FILE = Path(__name__).resolve().parent / 'my-virtual-pro-firebase-adminsdk-clovd-0a09b82ca0.json'


def firebase_client(cred_file):
    """Firebase クライアントを生成する"""
    cred = credentials.Certificate(cred_file)
    app = initialize_app(credential=cred)
    client = firestore.client(app=app)
    return client


def main():
    client = firebase_client(str(CRED_FILE))
    collection = client.collection("stats")
    for snapshot in collection.get():
        print(snapshot.id)
        doc_data = snapshot.to_dict()
        if 'rating' in doc_data:
            print('skip.')
            continue
        print('update.')
        attr = get_player_attr(doc_data)
        ovr = get_player_ovr(attr)
        collection.document(snapshot.id).update({
            'rating': {
                'ovr': ovr,
                'attr': attr,
            }
        })


if __name__ == '__main__':
    main()
