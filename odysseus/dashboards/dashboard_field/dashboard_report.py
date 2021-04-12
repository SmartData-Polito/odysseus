import datetime

from covid_19.dashboard_field.dashboard_chart import DashboardChart
import streamlit as st
from covid_19.dashboard_field.utils import articoli_regioni_no_in, transform_regions_pc_to_human, list_mesi

class DashboardReport(DashboardChart):

    def __init__(self, name, dati, regione):
        super().__init__(title="", name=name)
        self.regione=regione
        self.dati=dati

    def show_heading(self):
        #imposto il nome
        self.title = "Report del "+self.fornisci_data(self.dati)
        str1 = "Nel giorno "+self.fornisci_data(self.dati)+" si sono registrati "+str(int(self.dati.nuovi_positivi))+" casi "
        if self.regione in articoli_regioni_no_in:
            str1 = str1+articoli_regioni_no_in[self.regione]
        else:
            str1 = str1 + "in"
        str1 = str1 +" " + transform_regions_pc_to_human(regione=self.regione)+", portando il totale di attualmente positivi a "+str(int(self.dati.totale_attualmente_positivi))
        str1 = str1 + ". I decessi giornalieri ammontano a "+str(int(self.dati.nuovi_deceduti))+", il totale da inizio pandemia vale "+str(int(self.dati.totale_deceduti))+"."
        str1 = str1 +" In totale, al "+self.fornisci_data(self.dati)+", sono stati effettuati "+str(int(self.dati.tamponi_test_molecolare))+" tamponi molecolari e "+str(int(self.dati.tamponi_test_antigenico_rapido)) + " test antigenici rapidi."
        str1 = str1 + " Attualmente, il tasso di positività è pari al "+'{0:.3g}'.format(100.0*float(self.dati.tasso_positivi_tamponi))+"%."
        str1 = str1 + "\n Aprendo l'expander, è possibile visualizzare ulteriori dati sulla regione "+transform_regions_pc_to_human(regione=self.regione)+". "
        self.subtitle = str1

        super(DashboardReport, self).show_heading()
        exp = st.beta_expander("Apri per visualizzare le informazioni complete.")
        exp.dataframe(self.dati)

    def show(self):
        self.show_heading()


    def fornisci_data(self, dati):
        data = datetime.datetime.fromisoformat(str(dati.data))
        giorno = data.day
        mese = list_mesi[int(data.month)-1]
        anno = data.year

        return str(giorno)+" "+mese+" "+str(anno)
