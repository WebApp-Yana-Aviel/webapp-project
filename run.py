
import os
#from flask_script import Manager
#from flask_migrate import Migrate
from app import create_app


app = create_app(os.getenv('FLASK_ENV') or 'production')
#migrate = Migrate(create_app, db)
#manager = Manager(migrate)

if __name__ == '__main__':
    #manager = argparse.ArgumentParser()    
    #manager.run(debug=True,host='0.0.0.0',threaded=True)
    
    app.run(host='0.0.0.0',threaded=True,use_reloader=False)