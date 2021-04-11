from odysseus.webapp.apis import create_app
from odysseus.webapp.apis.api_cityDataManager.utils import *
import json

app = create_app()

def create_predefined_file(formato=["norm","raw"]):
    for f in formato:
        summary = summary_available_data(f)
        filename = os.path.join(
	    os.path.abspath(os.curdir),
        "odysseus","webapp","apis","api_cityDataManager",f"{f}-data.json"
        )
        with open(filename, 'w+') as f:
            json.dump(summary, f) 

if __name__ == '__main__':  # conditional only true if we run the script directly
    create_predefined_file()
    app.run(debug=True)

