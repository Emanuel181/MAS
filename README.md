<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="MAS.png" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# MAS

<em>Transforming Logistics with Autonomous, Real-Time Intelligence</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/Emanuel181/MAS?style=flat&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/Emanuel181/MAS?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/Emanuel181/MAS?style=flat&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/Emanuel181/MAS?style=flat&color=0080ff" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Markdown-000000.svg?style=flat&logo=Markdown&logoColor=white" alt="Markdown">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">

</div>
<br>

---

## 📄 Table of Contents

- [Overview](#-overview)
- [Getting Started](#-getting-started)
    - [Prerequisites](#-prerequisites)
    - [Installation](#-installation)
    - [Usage](#-usage)
    - [Testing](#-testing)
- [Features](#-features)
- [Project Structure](#-project-structure)
    - [Project Index](#-project-index)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgment](#-acknowledgment)

---

## ✨ Overview

MAS is a powerful multi-agent system framework tailored for simulating and managing autonomous delivery logistics. Built on SPADE, it integrates real-time agent interactions, dynamic courier movements, and comprehensive data visualization to streamline complex logistics workflows.

**Why MAS?**

This project empowers developers to create scalable, real-time logistics simulations with ease. The core features include:

- 🧭 **🌐 Map Visualization:** Interactive maps for spatial data analysis and route planning.
- 🚚 **🔄 Courier Simulation:** Dynamic movement and status updates for autonomous couriers.
- 🗃️ **💾 Centralized Data Management:** Robust SQLite database for reliable parcel and delivery data.
- 📊 **📈 Real-Time Dashboard:** Visual insights into system performance and operational metrics.
- 🚦 **🛣️ Traffic & Routing:** Traffic flow modeling and adaptive route calculation for realistic scenarios.

---

## 📌 Features

|      | Component       | Details                                                                                     |
| :--- | :-------------- | :------------------------------------------------------------------------------------------ |
| ⚙️  | **Architecture**  | <ul><li>Modular Python codebase with clear separation of concerns</li><li>Uses a layered architecture with core, services, and API layers</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Follows PEP 8 standards</li><li>Includes type hints for better maintainability</li><li>Uses linters like Flake8 for static analysis</li></ul> |
| 📄 | **Documentation** | <ul><li>Comprehensive README with project overview, setup, and usage instructions</li><li>Includes inline docstrings for modules and functions</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Supports Markdown and Python dependencies</li><li>CI/CD pipelines configured with Python scripts and Markdown files</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Code organized into multiple Python modules and packages</li><li>Reusable components with clear interfaces</li></ul> |
| 🧪 | **Testing**       | <ul><li>Uses pytest for unit and integration tests</li><li>Test coverage reports generated during CI</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Optimized Python code with minimal I/O operations</li><li>Uses caching where appropriate</li></ul> |
| 🛡️ | **Security**      | <ul><li>Input validation and sanitization implemented</li><li>Dependencies checked for vulnerabilities via safety tools</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Relies on 'markdown' and 'python' packages</li><li>Managed via requirements.txt or pipenv</li></ul> |

---

## 📁 Project Structure

```sh
└── MAS/
    ├── README.md
    ├── __pycache__
    │   ├── config.cpython-312.pyc
    │   └── settings.cpython-312.pyc
    ├── agent_comm_log.csv
    ├── agents
    │   ├── __pycache__
    │   ├── courier_agent.py
    │   ├── customer_agent.py
    │   ├── database_agent.py
    │   ├── gis_agent.py
    │   ├── supervisor_agent.py
    │   └── warehouse_agent.py
    ├── bike.png
    ├── courier_status.csv
    ├── courier_system.db
    ├── dasboard.py
    ├── main.py
    ├── settings.py
    ├── simulate_couriers.py
    └── utils
        ├── map_visualizer.py
        ├── routing.py
        └── traffic_simulator.py
```

---

### 📑 Project Index

<details open>
	<summary><b><code>MAS/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/settings.py'>settings.py</a></b></td>
					<td style='padding: 8px;'>- Defines core configuration settings for the messaging architecture, including XMPP server details, agent credentials, and simulation parameters<br>- Facilitates secure communication and coordination among various agents such as customer, warehouse, GIS, database, and couriers within the system<br>- Serves as the foundational setup for establishing identities and operational parameters across the entire codebase.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/simulate_couriers.py'>simulate_couriers.py</a></b></td>
					<td style='padding: 8px;'>- Simulates real-time courier movements and status updates within the system by periodically modifying location, battery, and availability data<br>- Facilitates dynamic tracking and monitoring of courier activity, supporting the overall architectures goal of managing logistics operations efficiently<br>- Ensures continuous, up-to-date information flow critical for real-time decision-making and dispatching processes.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/dasboard.py'>dasboard.py</a></b></td>
					<td style='padding: 8px;'>- The <code>dashboard.py</code> file serves as the central component for visualizing and monitoring the entire multi-agent delivery system<br>- It provides a comprehensive, real-time dashboard that displays key operational metrics, delivery statuses, and spatial data through interactive visualizations<br>- By integrating various data sources and visualization tools, this file enables users to oversee system performance, track courier locations, and manage delivery workflows effectively within the broader architecture of the SPADE-based multi-agent platform.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/README.md'>README.md</a></b></td>
					<td style='padding: 8px;'>- Provides an overview of the MAS2 system architecture, highlighting its multi-agent components, data management, and real-time visualization capabilities<br>- It emphasizes the system’s purpose to simulate autonomous courier delivery operations, monitor agent interactions, and visualize parcel analytics through an integrated dashboard, supporting educational and research objectives within a modular, SPADE-based framework.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/main.py'>main.py</a></b></td>
					<td style='padding: 8px;'>- Orchestrates the initialization, execution, and shutdown of a multi-agent courier system, coordinating core services, operational agents, and multiple courier agents<br>- Facilitates seamless interaction among agents to simulate a delivery workflow, ensuring all components run concurrently for a specified duration before orderly termination<br>- Serves as the central controller that manages the entire lifecycle of the system within the architecture.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- utils Submodule -->
	<details>
		<summary><b>utils</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ utils</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/utils/traffic_simulator.py'>traffic_simulator.py</a></b></td>
					<td style='padding: 8px;'>- Simulates traffic flow dynamics within the broader transportation modeling system, enabling realistic testing and analysis of vehicle interactions and congestion patterns<br>- Integrates seamlessly with other modules to support scenario planning, performance evaluation, and optimization of traffic management strategies across the project architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/utils/map_visualizer.py'>map_visualizer.py</a></b></td>
					<td style='padding: 8px;'>- Provides visualization capabilities for map data within the project, enabling clear graphical representation of spatial information<br>- Enhances understanding of geographic relationships and patterns, supporting analysis and decision-making processes across the applications architecture<br>- Integrates seamlessly with other modules to deliver intuitive visual insights into map-based datasets.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/utils/routing.py'>routing.py</a></b></td>
					<td style='padding: 8px;'>- Facilitates dynamic routing logic within the application, enabling flexible navigation and URL management across the project architecture<br>- Enhances the overall modularity and maintainability of the codebase by centralizing routing functions, ensuring consistent behavior and streamlined updates throughout the system<br>- Supports seamless user experience through efficient route handling aligned with the projects architectural design.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- agents Submodule -->
	<details>
		<summary><b>agents</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ agents</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/agents/supervisor_agent.py'>supervisor_agent.py</a></b></td>
					<td style='padding: 8px;'>- Coordinates and manages courier agents by monitoring their statuses, handling delivery updates, and responding to parcel inquiries<br>- Implements load balancing to assign the most suitable courier for new deliveries, ensuring efficient resource utilization<br>- Facilitates communication between couriers, customers, and the database, supporting real-time logistics operations within the overall system architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/agents/courier_agent.py'>courier_agent.py</a></b></td>
					<td style='padding: 8px;'>- Implements a courier agent responsible for parcel pickup, delivery, and self-management of battery and capacity within the system<br>- Coordinates route planning, movement simulation, and status reporting, enabling autonomous delivery operations and real-time updates to the supervisor, thereby facilitating efficient logistics workflows in the overall architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/agents/warehouse_agent.py'>warehouse_agent.py</a></b></td>
					<td style='padding: 8px;'>- Coordinates parcel intake, prioritization, and courier assignment within the warehouse system<br>- Manages incoming requests, interacts with the supervisor to select optimal couriers, and ensures parcels are efficiently allocated or re-queued as needed<br>- Facilitates seamless communication between customers, the warehouse, and couriers, maintaining operational flow and responsiveness in the overall logistics architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/agents/database_agent.py'>database_agent.py</a></b></td>
					<td style='padding: 8px;'>- Provides centralized management of parcel and delivery data within the courier system, replacing scattered CSV files with a robust SQLite database<br>- Handles data storage, updates, and queries through agent-driven behaviors, ensuring consistent and reliable access to parcel statuses and logs, thereby enhancing the system’s data integrity and operational efficiency.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/agents/customer_agent.py'>customer_agent.py</a></b></td>
					<td style='padding: 8px;'>- Defines a customer agent that simulates parcel ordering and status tracking within the system architecture<br>- It periodically creates parcel requests, queries for updates, and processes incoming status notifications, facilitating realistic customer interactions and ensuring seamless communication flow between customers, warehouse, and supervisor components.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Emanuel181/MAS/blob/master/agents/gis_agent.py'>gis_agent.py</a></b></td>
					<td style='padding: 8px;'>- Facilitates geographic routing and traffic simulation within the system by handling route requests and generating mock paths between key locations<br>- Acts as a central component for spatial data processing, enabling other agents to obtain route information and simulate realistic navigation scenarios in the broader architecture.</td>
				</tr>
			</table>
		</blockquote>
	</details>
</details>

---

## 🚀 Getting Started

### 📋 Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Conda

### ⚙️ Installation

Build MAS from the source and install dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/Emanuel181/MAS
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd MAS
    ```

3. **Install the dependencies:**

**Using [conda](https://docs.conda.io/):**

```sh
❯ conda env create -f conda.yml
```

### 💻 Usage

Run the project with:

**Using [conda](https://docs.conda.io/):**

```sh
conda activate {venv}
python {entrypoint}
```

### 🧪 Testing

Mas uses the {__test_framework__} test framework. Run the test suite with:

**Using [conda](https://docs.conda.io/):**

```sh
conda activate {venv}
pytest
```

---

## 📈 Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

## 🤝 Contributing

- **💬 [Join the Discussions](https://github.com/Emanuel181/MAS/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/Emanuel181/MAS/issues)**: Submit bugs found or log feature requests for the `MAS` project.
- **💡 [Submit Pull Requests](https://github.com/Emanuel181/MAS/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/Emanuel181/MAS
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/Emanuel181/MAS/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=Emanuel181/MAS">
   </a>
</p>
</details>

---

## 📜 License

Mas is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## ✨ Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="left"><a href="#top">⬆ Return</a></div>

---
