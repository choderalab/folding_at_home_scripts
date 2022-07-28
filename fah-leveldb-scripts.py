import plyvel
import pandas as pd
import subprocess
import re
import ast
import numpy as np
import matplotlib.pyplot as plt
import yaml, datetime
from argparse import ArgumentParser
import plotly.express as px
import plotly.express.colors as c

def get_args():
    parser = ArgumentParser()
    parser.add_argument("-d", "--date_file", type=str, default="dates.yaml")
    parser.add_argument("-p", "--projects_file", type=str, default="projects.yaml")
    parser.add_argument("-c", "--copy_db", type=bool, default=False)
    parser.add_argument("-a", "--analyze", type=bool, default=False)
    parser.add_argument("-s", "--server_name", type=str, default="pllwskifah1.mskcc.org")
    parser.add_argument("-i", "--server_id", type=str, default="SVR2359493832")
    args = parser.parse_args()
    return args

def copy_leveldb(server_name, server_id):
    date = datetime.date.today().strftime('%Y%m%d')
    server_path = f"server@{server_name}:~/server2/data/{server_id}/work.leveldb"
    local_leveldb_path = f"{server_id}_{date}_work.leveldb"
    print(f"Copying {server_path} to {local_leveldb_path}...")
    subprocess.Popen(f"rsync -ravh {server_path} {local_leveldb_path}", shell=True).wait()


def load_dates(date_file):
    with open(date_file) as f:
        date_list = yaml.safe_load(f)
    return date_list

class ProjectList():
    def __init__(self, projects_file, leveldb_path, date):
        self.projects_file = projects_file
        self.leveldb_path = leveldb_path
        self.project_list = []
        self.date = date
        with open(self.projects_file) as f:
            self.project_number_list = yaml.safe_load(f)
        self.make_project_list()

    def make_project_list(self):
        for project_number in self.project_number_list:
            project = Project(project_number, self.date)
            project.load_project_file()
            self.project_list.append(project)

    def load_leveldb(self):
        return plyvel.DB(self.leveldb_path, create_if_missing=False)

    def get_project_dfs(self):
        db = self.load_leveldb()
        for project in self.project_list:
            project.get_project_df(db)
        db.close()

    def report(self):
        for project in self.project_list:
            project.report()

    def make_complete_report(self):
        for project in self.project_list:
            print(project.project_number)
            project.report()
            project.report_success()
            project.plot_traj_lengths()
            # print(project.df)
            project.plot_histogram_by_run()
            print()



class Project():
    def __init__(self, project_number, date):
        self.project_number = project_number
        self.df = pd.DataFrame()
        self.project_file = f"p{project_number}-project.xml"
        self.date = date

    def load_project_file(self):
        file = open(self.project_file, "r")
        for line in file:
            if re.search("runs", line):
                myRegex = re.compile(r"[0-9]+")
                self.n_runs = int(myRegex.findall(line)[0])
            if re.search("clones", line):
                myRegex = re.compile(r"[0-9]+")
                self.n_clones = int(myRegex.findall(line)[0])
            if re.search("gens", line):
                myRegex = re.compile(r"[0-9]+")
                self.n_gens = int(myRegex.findall(line)[0])

    def get_project_df(self, db):
        l = []
        for key, value in db:
            if re.search(f"P{self.project_number}", str(key)):
                entry = db.get(key)
                entry = ast.literal_eval(entry.decode("UTF-8"))
                l.append(entry)
        self.df = self.df.append(l, ignore_index=True, sort=False)
        self.df['Traj length (ns)'] = self.df['gen'] * 10

    def report(self):
        print(f'{self.project_number} has {self.n_runs} runs with {self.n_clones} clones and {self.n_gens} gens')

    def report_success(self):
        finished_clones = self.df[np.logical_and(self.df.gen == self.n_gens, self.df.state == "FINISHED")].shape[0]
        print(
            f"Finished {finished_clones} clones which is {100 * finished_clones / self.n_runs / self.n_clones:3.1f} % of clones."
        )
        finished_WU = np.sum(self.df.gen)
        print(
            f"Finished {finished_WU} WU which is {100 * finished_WU / self.n_runs / self.n_clones / self.n_gens:3.1f} % of clones."
        )

        failed_clones = self.df[self.df.state == "FAILED"].shape[0]
        print(
            f"Failed {failed_clones} clones which is {100 * failed_clones / self.n_runs / self.n_clones:3.1f} % of clones."
        )
        assigned_clones = self.df[self.df.state == "ASSIGNED"].shape[0]
        print(
            f"Assigned {assigned_clones} clones which is {100 * assigned_clones / self.n_runs / self.n_clones:3.1f} % of clones."
        )

    def plot_traj_lengths(self):
        wu_length = 10  # in ns
        traj_lengths_ns = self.df['gen'].values * wu_length
        plt.figure(figsize=(10, 10))
        plt.hist(traj_lengths_ns, range=(0, traj_lengths_ns.max()), bins=25)
        plt.xlabel("Traj length (ns)")
        plt.ylabel("Number of CLONEs")
        plt.xlim([0, 5000])
        plt.title(f"p{self.project_number}: " + str(traj_lengths_ns.sum() / 1000) + " $\mu$s")
        plt.savefig(f"{self.date}_p{self.project_number}-traj-distribution.png", dpi=300)
        return traj_lengths_ns

    def plot_histogram_by_run(self):
        palecyan = (0.8, 1.0, 1.0)
        wheat = (0.99, 0.82, 0.65)
        def get_rbg_str_from_pymol_colors(pymol_color):
            return px.colors.label_rgb(px.colors.convert_to_RGB_255(pymol_color))

        fig = px.histogram(self.df,
                           x='Traj length (ns)',
                           color='run',
                           # title=f'p{project_number}: {str(traj_length_df.sum()/1000)} µs',
                           #                    title="Distribution of Trajectories on Folding@home by Starting State",
                           color_discrete_sequence=[c.qualitative.Safe[0],
                                                    get_rbg_str_from_pymol_colors(wheat)],
                           labels={"run": "<b>Run</b>"}
                           )
        fig.update_xaxes(range=[0, 5000])
        fig.update_yaxes(range=[0, 40])
        fig.update_layout(height=900,
                          width=1200,
                          barmode='overlay',
                          font=dict(size=36,
                                    family="Helvetica"),
                          plot_bgcolor="#FFF",  # Sets background color to white
                          xaxis=dict(
                              title="<b>Trajectory Length (ns)</b>",
                              linecolor="#BCCCDC",  # Sets color of X-axis line
                              showgrid=False  # Removes X-axis grid lines
                          ),
                          yaxis=dict(
                              title="<b># of Trajectories</b>",
                              linecolor="#BCCCDC",  # Sets color of Y-axis line
                              showgrid=False,  # Removes Y-axis grid lines
                          )
                          )
        fig.update_traces(opacity=0.7,
                          xbins={'size': 50},
                          #                  marker=dict(size=20)
                          )
        # fig.update_traces(xbins={'size':50})
        # trace_names = ["<b>Open State</b>", "<b>Closed State</b>"]
        trace_names = ["Open State", "Closed State"]
        for idx, name in enumerate(trace_names):
            fig.data[idx].name = name
            fig.data[idx].hovertemplate = name

        fig.update_layout(legend=dict(
            yanchor="bottom",
            y=0.01,
            xanchor="right",
            x=0.99,
            font=dict(size=48, family='Helvetica'),
            itemsizing='constant',
            #     markersize=20

        ))

        # fig.update_layout(legend=dict(
        #     yanchor="top",
        #     y=0.99,
        #     xanchor="right",
        #     x=0.99
        # ))

        fig.show()
        fig.write_image(f"{self.date}_p{self.project_number}_distribution_by_state.png")

if __name__ == "__main__":
    args = get_args()
    date_list = load_dates(args.date_file)
    print(date_list)

    if args.copy_db:
        # leveldb_path = f"SVR2359493832_{date}_work.leveldb/work.leveldb"
        copy_leveldb(args.server_name, args.server_id)

    for date in date_list:
        leveldb_path = f"{args.server_id}_{date}_work.leveldb/work.leveldb"
        #subprocess.Popen(f"rm {leveldb_path}/LOCK", shell=True).wait()
        if args.analyze:
            project_list = ProjectList(args.projects_file, leveldb_path, date)
            project_list.report()
            project_list.load_leveldb()
            project_list.get_project_dfs()
            project_list.make_complete_report()

        #make_fah_progress_images(date, project_list)




