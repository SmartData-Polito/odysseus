from odysseus.webapp.apis import create_app
from odysseus.webapp.apis.api_cityDataManager.utils import *
import json

app = create_app()


if __name__ == '__main__':  # conditional only true if we run the script directly
    create_predefined_file(DEBUG=False)
    app.run(debug=True)