import os

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
matplotlib.rcParams["axes.grid"] = True

import seaborn as sns

from e3f2s.utils.time_utils import *

SMALL_SIZE = 8
MEDIUM_SIZE = 12
BIGGER_SIZE = 20

plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


class EFFCS_SimOutputPlotter ():

	def __init__ (self, simOutput, city, sim_scenario_name):

		self.simOutput = simOutput
		self.city = city
		self.grid = simOutput.grid
		self.sim_scenario_name = sim_scenario_name

		model_general_conf_string = "_".join([
			str(v) for v in simOutput.sim_general_conf.values()]
		).replace("'", "").replace(".", "d")
		model_conf_string = "_".join([
			str(v) for v in simOutput.sim_scenario_conf.values()]
		).replace("'", "").replace(".", "d")
		self.figures_path = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			"figures",
			city,
			"single_run",
			sim_scenario_name,
		)
		os.makedirs(self.figures_path, exist_ok=True)

		self.sim_booking_requests = simOutput.sim_booking_requests

		self.sim_bookings = simOutput.sim_bookings

		self.sim_charges = simOutput.sim_charges

		self.sim_not_enough_energy_requests = pd.DataFrame(simOutput.sim_not_enough_energy_requests)

		self.sim_no_close_vvehicle_requests = pd.DataFrame(simOutput.sim_no_close_vehicle_requests)

		self.sim_unsatisfied_requests = simOutput.sim_unsatisfied_requests

		self.sim_system_charges_bookings = simOutput.sim_system_charges_bookings

		self.sim_users_charges_bookings = simOutput.sim_users_charges_bookings

		self.sim_vehicles_events = pd.concat([
			self.sim_bookings, self.sim_charges
		], ignore_index=True, sort=False).sort_values("start_time")

		self.sim_charge_deaths = simOutput.sim_charge_deaths

		self.simOutput = simOutput

	def plot_city_zones(self):

		fig, ax = plt.subplots(1, 1, figsize=(15, 15))
		plt.title("")
		plt.xlabel(None)
		plt.xticks([])
		plt.ylabel(None)
		plt.yticks([])
		self.grid.plot(color="white", edgecolor="black", ax=ax)
		self.grid.plot(color="lavender", edgecolor="blue", column="valid", ax=ax).plot()
		plt.savefig(os.path.join(self.figures_path, "city_zones.png"), transparent=True)
		plt.close()

	def plot_charging_infrastructure(self):

		fig, ax = plt.subplots(1, 1, figsize=(15, 15))
		plt.title("")
		plt.xlabel(None)
		plt.xticks([])
		plt.ylabel(None)
		plt.yticks([])
		self.grid.plot(color="white", edgecolor="black", ax=ax)
		self.grid.plot(color="lavender", edgecolor="blue", column="valid", ax=ax).plot()

		if self.simOutput.sim_scenario_conf["hub"]:
			self.grid.plot(color="white", edgecolor="black", ax=ax)
			self.grid.plot(color="lavender", edgecolor="blue", column="valid", ax=ax).plot()
			self.grid.loc[[self.simOutput.sim_stats["hub_zone"]]].plot(ax=ax)
			plt.savefig(os.path.join(self.figures_path, "hub_location.png"), transparent=True)
			plt.close()

		elif self.simOutput.sim_scenario_conf["distributed_cps"]:

			charging_zones = pd.Index(self.sim_charges.zone_id.unique())
			charging_poles_by_zone = self.sim_charges.zone_id.value_counts()
			self.grid.loc[charging_zones, "poles_count"] = charging_poles_by_zone
			self.grid.plot(color="white", edgecolor="black", ax=ax)
			self.grid.loc[self.simOutput.sim.simInput.valid_zones].plot(column="poles_count", ax=ax).plot()
			self.grid.loc[charging_zones].plot(ax=ax)
			plt.savefig(os.path.join(self.figures_path, "cps_locations.png"), transparent=True)
			plt.close()

	def plot_events_profile_barh (self):

		fig, ax = plt.subplots(figsize=(15, 5))
		plt.title("fraction of events, single simulation")
		pd.DataFrame([
			pd.Series([
				self.simOutput.sim_stats["fraction_same_zone_trips_satisfied"],
				self.simOutput.sim_stats["fraction_not_same_zone_trips_satisfied"]
			], index=["same zone", "neighbor zone"], name="satisfied %"),
			pd.Series([
				self.simOutput.sim_stats["fraction_no_close_vehicles_unsatisfied"],
				self.simOutput.sim_stats["fraction_deaths_unsatisfied"]
			], index=["no close vehicle", "not enough energy"], name="unsatisfied %"),
			pd.Series([
				self.simOutput.sim_stats["fraction_unsatisfied"],
				self.simOutput.sim_stats["fraction_satisfied"]
			], index=["unsatisfied", "satisfied"], name="events %"),
		]).plot.barh(stacked=True, ax=ax)

		plt.tight_layout()
		plt.savefig(os.path.join(self.figures_path, "events_profile.png"), transparent=True)
		# plt.show()
		plt.close()

	def plot_events_t (self):

		plt.figure(figsize=(15, 5))
		self.sim_booking_requests.fillna(0).set_index("start_time").iloc[:, 0].resample("60Min").count().plot(
			label="requests", linewidth=2, alpha=0.7
		)
		self.sim_bookings.set_index("start_time").iloc[:, 0].resample("60Min").count().plot(
			label="bookings", linewidth=2, alpha=0.7
		)
		self.sim_unsatisfied_requests.set_index("start_time").iloc[:, 0].resample("60Min").count().plot(
			label="unsatisfied", linewidth=2, alpha=0.7
		)
		self.sim_charges.set_index("start_time").iloc[:, 0].resample("60Min").count().plot(
			label="charges", linewidth=2, alpha=0.7
		)
		plt.legend()
		plt.xlabel("t")
		plt.ylabel("n_events")
		plt.savefig(os.path.join(self.figures_path, "events_profile_t.png"), transparent=True)
		# plt.show()
		plt.close()

	def plot_fleet_status_t (self):

		for col in [
			"n_vehicles_available", "n_vehicles_charging_system", "n_vehicles_charging_users", "n_vehicles_booked"
		]:
			plt.figure(figsize=(15, 5))
			self.sim_booking_requests.set_index("start_time")[col].plot(
				label=col, linewidth=2, alpha=0.7
			)
			plt.legend()
			plt.xlabel("t")
			plt.ylabel("n_vehicles")
			plt.savefig(os.path.join(self.figures_path, col + "_profile.png"), transparent=True)
			# plt.show()
			plt.close()

	def plot_events_hourly_count_boxplot (self, which_df, start_or_end):

		if which_df == "bookings":
			df = self.sim_bookings
		if which_df == "charges":
			df = self.sim_charges
		if which_df == "unsatisfied":
			df = self.sim_unsatisfied_requests
		if which_df == "no_close_vehicle":
			df = self.sim_no_close_vehicle_requests
		if which_df == "not_enough_energy":
			df = self.sim_not_enough_energy_requests

		df = get_time_group_columns(df)
		trips_df_norm_count = get_time_grouped_hourly_count(
			df, start_or_end, which_df
		)
		trips_df_norm_count.hour = trips_df_norm_count.hour.astype(int)

		plt.figure(figsize=(15, 5))
		sns.boxplot(x="hour", y="_".join([which_df, "hourly", start_or_end, "count"]), data=trips_df_norm_count)
		sns.swarmplot(x="hour", y="_".join([which_df, "hourly", start_or_end, "count"]), data=trips_df_norm_count, color="black")
		plt.savefig(
			os.path.join(
				self.figures_path, "_".join([which_df, "hourly", start_or_end, "count", "boxplot.png"])
			), transparent=True
		)
		# plt.show()
		plt.close()

	def plot_events_hourly_count_boxplot (self, which_df, start_or_end):

		if which_df == "bookings":
			df = self.sim_bookings
		if which_df == "charges":
			df = self.sim_charges
		if which_df == "unsatisfied":
			df = self.sim_unsatisfied_requests
		if which_df == "no_close_vehicle":
			df = self.sim_no_close_vehicle_requests
		if which_df == "not_enough_energy":
			df = self.sim_not_enough_energy_requests

		df = get_time_group_columns(df)
		trips_df_norm_count = get_time_grouped_hourly_count(
			df, start_or_end, which_df
		)
		trips_df_norm_count.hour = trips_df_norm_count.hour.astype(int)

		plt.figure(figsize=(15, 5))
		sns.boxplot(x="hour", y="_".join([which_df, "hourly", start_or_end, "count"]), data=trips_df_norm_count)
		sns.swarmplot(x="hour", y="_".join([which_df, "hourly", start_or_end, "count"]), data=trips_df_norm_count, color="black")
		plt.savefig(
			os.path.join(
				self.figures_path, "_".join([which_df, "hourly", start_or_end, "count", "boxplot.png"])
			), transparent=True
		)
		# plt.show()
		plt.close()

	def plot_n_vehicles_charging_hourly_mean_boxplot(self):

		df = get_time_group_columns(self.sim_booking_requests)
		trips_df_norm_count = get_time_grouped_hourly_mean(
			df, "start", "n_vehicles_charging_system", "n_vehicles_charging_system"
		)
		trips_df_norm_count.hour = trips_df_norm_count.hour.astype(int)

		plt.figure(figsize=(15, 5))
		sns.boxplot(
			x="hour", y="_".join(["n_vehicles_charging_system", "hourly", "mean"]),
			data=trips_df_norm_count
		)
		sns.swarmplot(
			x="hour", y="_".join(["n_vehicles_charging_system", "hourly", "mean"]),
			data=trips_df_norm_count, color="black"
		)
		plt.savefig(
			os.path.join(
				self.figures_path, "_".join(["n_vehicles_charging_system", "hourly", "mean", "boxplot.png"])
			), transparent=True
		)

	def plot_hourly_relocost_boxplot (self):

		table = self.sim_charges.pivot_table\
			(index=["date"], columns=["hour"], values=["vehicle"], aggfunc=np.sum)\
			.fillna(0.0).loc[:, "vehicle"] / 3600

		plt.figure()
		table.reset_index().boxplot(column=list(table.columns))
		plt.title("relocation cost hourly boxplot")
		plt.xlabel("hour")
		plt.ylabel("relocation cost [hours]")
		plt.savefig(os.path.join(self.figures_path, "relocost_hourly_boxplot.png"), transparent=True)
		# plt.show()
		plt.close()

	def plot_choropleth (self, col):

		fig, ax = plt.subplots(1, 1, figsize=(15,15))
		self.grid.dropna(subset=[col]).plot(column=col, ax=ax, legend=True)
		plt.xlabel(None)
		plt.xticks([])
		plt.ylabel(None)
		plt.yticks([])
		plt.title(col + " chorophlet map")
		plt.savefig(
			os.path.join(
				self.figures_path,
				"_".join([col, "clorophlet", "map.png"])
			), transparent=True
		)
		plt.close()
