def insert_costs(df,scenario_costs_conf, administrative_cost_conf, vehicles_cost_conf, poles_cost_conf):
    df['relocation_cost'] = round((1.25*2*df.cum_relo_t/(90*8)))*(administrative_cost_conf['relocation_workers_hourly_cost']*8*7)*52 # (10 worker * costo del lavoro orario * ore * giorni)
    df['cars_cost'] = (df.n_cars)*(vehicles_cost_conf['car_annual_cost'] + vehicles_cost_conf['car_annual_insurance_cost'] + vehicles_cost_conf['car_annual_mantenaince_cost'])
    df['poles_cost'] = df.n_charging_poles*(poles_cost_conf['pole_installation_cost']+ poles_cost_conf['pole_annual_mantenaince_cost'] + poles_cost_conf['cosap_annual_tax'])
    df['energy_cost'] = df.tot_charging_energy*scenario_costs_conf['kwh_cost']
    df['revenues'] = (df.total_trips_duration*scenario_costs_conf['real_bookings_percentage']/100)*scenario_costs_conf['price_per_minute']
    df['charge_deaths_cost'] = df.n_charge_deaths*scenario_costs_conf['tow_truck_cost_per_call']
    df['deaths_cost'] = df.n_deaths*scenario_costs_conf['tow_truck_cost_per_call']
    df['office_cost'] = administrative_cost_conf['office_costs']
    df['customer_service_cost'] = administrative_cost_conf['n_customer_service_specialists']*administrative_cost_conf['customer_service_specialist_ral']
    df['marketing_cost'] = df.revenues*administrative_cost_conf['marketing_on_revenues_percentage']/100
    df['manager_salary'] = administrative_cost_conf['n_manager']*administrative_cost_conf['manager_ral']
    df['washing'] = vehicles_cost_conf['disinfection_cost']*df.n_charges + vehicles_cost_conf['washing_cost']*df.n_bookings/100
    df['it_salary'] = administrative_cost_conf['n_it_specialists']*administrative_cost_conf['it_specialist_ral']
    df['administrative_costs'] = df.office_cost + df.manager_salary + df.it_salary + df.customer_service_cost
    df['fixed_costs'] = df.cars_cost + df.poles_cost  + df.customer_service_cost+ df.office_cost + df.manager_salary+ df.it_salary
    df['variabile_costs'] = df.relocation_cost + df.energy_cost + df.charge_deaths_cost + df.deaths_cost + df.washing + df.marketing_cost
    df['utile'] = df.revenues - df.washing - df.energy_cost -df.relocation_cost - df.cars_cost- df.poles_cost  - df.charge_deaths_cost- df.deaths_cost - df.office_cost - df.customer_service_cost- df.marketing_cost - df.manager_salary - df.it_salary