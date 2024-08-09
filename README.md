# The Growing Demand for Building Modeling

The increasing demand for building modeling is driven by the need to decarbonize and transition towards a decentralized power grid. This shift leverages technologies such as distributed energy resources and energy storage systems at the Grid Edge. By integrating advanced automation, buildings can optimize energy usage, manage local solar, battery storage, electric vehicles, and thermal storage, and provide demand-side energy management, thereby supporting broader grid operations.

Energy simulations enable accurate predictions of building responses, which are essential for analysis, design, and the development of control algorithms. Additionally, high-fidelity building simulations can generate synthetic data, crucial for training state-of-the-art machine learning models across various components of the building ecosystem.

# Current State of Software

Current tools for building modeling, such as EnergyPlus, meet the demand for detailed energy consumption simulations but are often limited by their complexity and steep learning curve. EnergyPlus simulates almost all components in a building ecosystem with utmost detail, increasing the need for expertise and contributing to the steep learning curve. Moreover, the way EnergyPlus provides data output is not conducive to instant data analysis, and the lack of an in-built data visualization tool further complicates the analysis process.

# Our Data Management Tool

To address these challenges, we have developed a solution that builds on top of EnergyPlus, requiring less expertise and offering a shallow learning curve. Our application automates data generation, aggregation, and visualization using EnergyPlus, significantly simplifying the process. Additionally, we provide an architecture for a relational database that stores generated and aggregated data in a manner that facilitates easy analysis. This approach not only streamlines the use of EnergyPlus but also enhances its usability by addressing its complexity, making data analysis more efficient.

# GUI-Based Application

We offer a user-friendly, GUI-based interface for conducting energy simulations through EnergyPlus, allowing users to customize options for building type, climate, and schedules, all powered by the Opyplus library. The application, built entirely in Python using Plotly-Dash, provides interfaces for data generation, aggregation, and visualization, making the entire process more intuitive and efficient.

![Schematic of the GUI-Based Application](# "Fig 1: Schematic of the GUI-Based Application")

### Data Generation

The Data Generation interface enables users to input their own IDF files or select from the PNNL database, which consists of prototypical commercial, manufactured, and residential building IDF files. Users can customize the time-step, period, and reporting frequency, as well as modify schedules for people and equipment. We've preselected 35 variables essential for approximating building power consumption, but users can select their own. The output is provided as a well-formatted pickle file containing a dictionary, with pandas DataFrames as values for each generated variable, making it easy to integrate into data analysis workflows.

![Data Generation GIF](# "Data Generation App")

### Data Aggregation

The Data Aggregation interface simplifies complex building models with multiple thermal zones by collapsing them into a single-zone, reduced-order, lightweight model. While a single-zone model offers simplicity, it may not provide sufficient accuracy for buildings with many zones. Users can choose to aggregate the original model into a single zone or define custom aggregation zones. Additionally, users can select from three aggregation methods: average, weighted average based on zone floor area, or weighted average based on zone volume.

![Data Aggregation GIF](# "Data Aggregation App")

### Data Visualization

The Data Visualization interface allows users to generate time-series plots for any generated or aggregated variable and create scatter plots to explore relationships between two variables. Additionally, users can generate basic statistics, histograms, and distribution parameters for any variable, enabling comprehensive data analysis.

![Data Visualization GIF](# "Data Visualization App")

![Visualizing Zone Temperatures in the Visualization App](# "Fig 2: Visualizing Zone Temperatures in the Visualization App")

![Schematic of the Database](# "Fig 3: Schematic of the Database")

# Data Management Capabilities

Our application includes a comprehensive database that organizes extensive pre-simulated data for easy access and scalable updates. This database features three linked tables: one detailing building prototypes, another containing time-series data from simulations, and a third storing additional zone information from EIO files. The structure of this database enables efficient data retrieval, making it highly suitable for various analysis tasks and machine learning workflows within the buildings domain, thereby enhancing the overall functionality and usability of the application.

# Summary

Our application, built on EnergyPlus, provides a streamlined solution for data generation, aggregation, and visualization, along with a robust database structure for efficient data storage and retrieval. This infrastructure not only aids in the analysis of building simulation data but also supports advanced machine learning workflows within the buildings domain. Our tool simplifies building energy simulations, offers a comprehensive platform for data management, and enhances data analytics capabilities, making it easier to adopt energy-efficient building designs and technologies. By leveraging the demand flexibility of buildings, our tool contributes to improved grid stability, supporting the transition to a more sustainable energy future.
