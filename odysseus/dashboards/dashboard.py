from odysseus.dashboards.dashboard_field.dashboard_main import DashboardMain
# from odysseus.dashboards.dashboard_field.screen_principale import ScreenPrincipale

#from e3f2s.utils.st_html_utils import _max_width_

def load_dashboard():



    # available_fields = [ScreenPrincipale(title="TITOLO", name="CityDataManager",month = 10, year = 2017, city = "Torino" )]
    DashboardMain(title="Benvenuti nella dashboard Odysseus",
                  available_fields = [],
                  logo="https://smartdata.polito.it/wp-content/uploads/2017/10/logo_official.png").show()

