from e3f2s.webapp.apis import create_app


app = create_app()

if __name__ == '__main__':  # conditional only true if we run the script directly
    app.run(debug=True)

