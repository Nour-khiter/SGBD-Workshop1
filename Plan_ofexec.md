# CivicPulse
## Project Execution Plan, Team Responsibilities & Deliverables

**Course:** Advanced SQL  
**Project:** Applied Data Analytics & Decision Support  
**Team size:** 4 members  
**Estimated remaining time:** 2–3 days  
**Dashboard technology:** Microsoft Power BI  
**Database technology:** PostgreSQL  
**Dataset:** NYC 311 Service Requests (2020–Present)

---

## 1. Project Overview

CivicPulse is a data-driven decision-support portal designed to help municipal decision-makers understand public service demand, monitor service performance, identify geographic disparities and support better resource allocation.

Using the NYC 311 Service Requests dataset, the project will transform raw service-request records into meaningful information through PostgreSQL data modeling, SQL analysis and an interactive Power BI dashboard.

The objective is not simply to visualize data, but to demonstrate how a relational database and analytical SQL queries can support practical administrative decisions.

### Main objectives

1. Analyze the distribution of public service requests across different geographic areas.
2. Monitor service demand and identify changes over time.
3. Evaluate service resolution times and outstanding requests.
4. Identify potential operational bottlenecks and resource-allocation priorities.
5. Present actionable findings through an interactive dashboard.

### Main analytical questions

- Which boroughs experience the highest number of service requests and outstanding requests?
- Which complaint categories have the longest median resolution times?
- How does service demand evolve over time?
- Which agencies have the largest workloads and backlogs?
- What actions could municipal managers take based on these observations?

---

## 2. Team Organization and Responsibilities

The project will be divided into four workstreams. Each member will have primary ownership of one component, while all members remain responsible for reviewing and understanding the complete project.

### Member 1 — Data Acquisition & Data Quality Lead

**Main responsibility:** Ensure that the project uses reliable, documented and properly prepared data.

Tasks:

- Inspect the official NYC Open Data source and its data dictionary.
- Determine the extraction period and select a manageable dataset sample, targeting approximately 30,000 records.
- Download and organize the raw dataset.
- Inspect the dataset for missing values, duplicates, inconsistent formats and invalid dates.
- Identify important data-quality limitations.
- Coordinate with the database member to agree on column names and data types.
- Document the data source, extraction date, selected period and preparation procedures.
- Help validate the final analytical results.

**Expected deliverables:**

- Original CSV dataset.
- Data dictionary.
- Data-quality report.
- Documentation of data extraction and preparation.
- Validation notes.

**Success criterion:** The team has a documented and consistent dataset that can be loaded into PostgreSQL without unexplained data inconsistencies.

### Member 2 — Database Architecture & SQL Lead

**Main responsibility:** Design and implement the PostgreSQL database and develop the analytical SQL queries.

Tasks:

- Design the relational database schema.
- Prepare the Entity-Relationship Diagram (ERD).
- Create the required tables and relationships.
- Define primary keys, foreign keys, constraints and appropriate data types.
- Load the prepared dataset into PostgreSQL.
- Verify referential integrity and table relationships.
- Develop the SQL queries needed to answer the project's analytical questions.
- Use joins, aggregations, subqueries, CTEs and window functions where appropriate.
- Create useful views for Power BI integration.
- Organize the SQL scripts and ensure they can be executed again.

**Proposed database structure:**

1. `service_requests` — central table containing request records and their associated foreign keys.
2. `problems` — complaint categories and descriptors.
3. `agencies` — agency identifiers and names.
4. `locations` — boroughs, ZIP codes and available geographic information.

**Expected deliverables:**

- PostgreSQL database.
- Database creation and loading scripts.
- ERD.
- Analytical SQL scripts.
- Validated query results and views.

**Success criterion:** The database is properly structured, populated and capable of producing reliable analytical results.

### Member 3 — Power BI & Dashboard Development Lead

**Main responsibility:** Transform the validated SQL results into an interactive decision-support dashboard.

Tasks:

- Define the dashboard's visual structure and navigation.
- Connect Power BI to the PostgreSQL database.
- Configure relationships and verify the imported data.
- Define the necessary measures and calculated indicators.
- Develop KPI cards, charts, tables, filters and geographic visualizations.
- Ensure that the dashboard is readable and understandable to non-technical decision-makers.
- Test filters and interactions.
- Validate dashboard figures against PostgreSQL query results.
- Prepare a short demonstration of the dashboard.

**Proposed dashboard pages:**

**Page 1 — Citywide Overview**
- Total service requests.
- Outstanding requests.
- Median resolution time.
- Monthly service-request trends.
- Most frequent complaint categories.

**Page 2 — Geographic Analysis**
- Request distribution by borough.
- Open requests by geographic area.
- Geographic concentration of service demand.
- Filters for borough and time period.

**Page 3 — Service Performance**
- Median resolution time by complaint category.
- Agency workload distribution.
- Requests by agency and status.
- Comparisons of service performance.

**Expected deliverables:**

- Power BI `.pbix` file.
- Three functional dashboard pages.
- KPI definitions and measures.
- Dashboard screenshots.
- Demonstration-ready dashboard.

**Success criterion:** The dashboard accurately reflects the SQL analysis and allows users to explore the results interactively.

### Member 4 — Analytics, Architecture & Presentation Lead

**Main responsibility:** Coordinate the analytical narrative and communicate the project's value to its audience.

Tasks:

- Finalize the problem statement and decision-support objectives.
- Identify the target users and decisions supported by CivicPulse.
- Prepare the system architecture diagram.
- Coordinate the interpretation of analytical SQL results.
- Identify three important findings supported by actual data.
- Translate findings into practical recommendations.
- Prepare the AI-generated dashboard comparison using the same dataset and problem.
- Document the AI tool and exact prompt used.
- Compare the AI dashboard against the team's dashboard.
- Coordinate the presentation slides and ensure consistency across sections.
- Organize the final rehearsal.

**Expected deliverables:**

- Problem statement and project objectives.
- Architecture diagram.
- Three analytical findings.
- Recommendations and expected benefits.
- AI dashboard comparison.
- Final presentation.

**Success criterion:** The project tells a coherent story, moving from a real-world problem to data analysis, insights and actionable recommendations.

---

## 3. Execution Schedule

The team will follow a three-day execution plan. If the deadline requires submission after only two days, the final stage will be compressed and non-essential improvements will be removed.

### DAY 1 — Project Foundation

**Main objective:** Establish the data, database and project structure.

| Member | Tasks |
|---|---|
| Member 1 | Inspect the dataset, select the extraction period, download the sample and perform initial data-quality checks. |
| Member 2 | Finalize the ERD, create the four PostgreSQL tables, define relationships and begin loading the data. |
| Member 3 | Define the dashboard wireframe, select the KPIs and investigate PostgreSQL connectivity from Power BI. |
| Member 4 | Finalize the problem statement, analytical questions, target audience and architecture diagram. |

**End-of-day milestones:**

- Dataset selected and documented.
- Initial data-quality inspection completed.
- ERD and database schema approved.
- PostgreSQL tables created and populated.
- Dashboard wireframe prepared.
- Problem statement and architecture diagram drafted.

**Day 1 deliverables:** Raw dataset, data dictionary, initial quality report, ERD, PostgreSQL schema and architecture diagram.

### DAY 2 — SQL Analysis & Dashboard Development

**Main objective:** Transform the database into validated insights and a functional dashboard.

| Member | Tasks |
|---|---|
| Member 1 | Complete data-quality checks, document missing values and validate the consistency of the loaded records. |
| Member 2 | Develop and test the analytical SQL queries, joins, aggregations and views. |
| Member 3 | Connect Power BI to PostgreSQL and implement the three dashboard pages. |
| Member 4 | Interpret query results, identify three findings and formulate initial recommendations. |

**Priority SQL analyses:**

1. Monthly request volume and demand evolution.
2. Request distribution by borough.
3. Outstanding requests by borough.
4. Median resolution time by complaint category.
5. Agency workload and request status distribution.

**End-of-day milestones:**

- Core SQL queries execute correctly.
- Data relationships and calculations are validated.
- Power BI successfully connects to PostgreSQL.
- Three dashboard pages are functional.
- Initial analytical findings are identified.
- AI comparison prompt is prepared.

**Day 2 deliverables:** Validated SQL scripts, query outputs, functional Power BI dashboard and preliminary findings.

### DAY 3 — Finalization & Presentation

**Main objective:** Complete the decision-support analysis and prepare the final submission.

| Member | Tasks |
|---|---|
| Member 1 | Finalize data documentation and audit the dataset and preparation decisions. |
| Member 2 | Organize SQL scripts, verify database reproducibility and perform final query checks. |
| Member 3 | Polish the dashboard, test interactions, validate KPI figures and prepare the demonstration. |
| Member 4 | Complete the AI comparison, finalize recommendations, integrate presentation slides and coordinate rehearsal. |

**End-of-day milestones:**

- Dashboard finalized and tested.
- AI-generated dashboard and comparison documented.
- Three findings and recommendations finalized.
- SQL scripts organized and executable.
- Presentation completed.
- All team members have rehearsed their contributions.

**Day 3 deliverables:** Final database, SQL scripts, Power BI dashboard, AI comparison evidence and presentation.

---

## 4. Task Dependencies and Coordination

Certain tasks depend on the completion of other tasks. The team should respect the following execution order:

1. **Dataset selection and inspection:** Member 1 establishes the data source, columns and extraction period.
2. **Database design:** Members 1 and 2 agree on the column mapping and finalize the relational model.
3. **Database implementation:** Member 2 creates and populates the PostgreSQL database.
4. **SQL validation:** Member 2 develops the queries, with Member 1 reviewing the underlying data assumptions.
5. **Dashboard integration:** Member 3 connects Power BI to the validated database and implements the KPIs.
6. **Analytical interpretation:** Member 4 works with the team to interpret the actual query results.
7. **AI comparison:** Member 4 evaluates an AI-generated dashboard using the same dataset and problem.
8. **Final integration:** All members review the database, SQL analysis, dashboard and presentation together.

Some work can happen in parallel. For example, the dashboard wireframe, architecture diagram and presentation outline can be prepared before the database is fully implemented.

However, final dashboard figures and analytical conclusions must be based on validated data.

---

## 5. Main Analytical Indicators

The team should prioritize the following indicators:

| Indicator | Purpose |
|---|---|
| Total requests | Measure overall service demand. |
| Open requests | Monitor outstanding workload. |
| Median resolution time | Understand typical resolution duration for closed requests. |
| Closure rate | Evaluate the proportion of requests closed within a clearly defined cohort. |
| Overdue requests | Identify requests past their due date when valid due-date information exists. |
| Monthly request volume | Monitor demand evolution. |

Resolution-time calculations must exclude open requests and invalid date intervals. Recent requests should also be considered carefully because they have had less time to be resolved.

---

## 6. AI-Generated Dashboard Comparison

The project requires a comparison between the team's dashboard and one generated using an AI tool.

The comparison should use:

- The same dataset.
- The same database schema or equivalent field definitions.
- The same decision-support problem.
- A documented AI prompt.

The team should evaluate:

1. Relevance of selected KPIs.
2. Correctness of calculations and data interpretation.
3. Visual clarity and organization.
4. Quality of geographic and operational analysis.
5. Usefulness for actual decision-making.

The comparison must identify both the strengths of the AI-generated dashboard and the elements requiring correction or redesign.

---

## 7. Final Deliverables

The following items must be ready before submission:

| Deliverable | Responsible member |
|---|---|
| Raw dataset and data dictionary | Member 1 |
| Data-quality report | Member 1 |
| PostgreSQL database with four related tables | Member 2 |
| Database creation/loading scripts | Member 2 |
| ERD | Member 2 |
| Analytical SQL queries | Member 2 |
| Power BI dashboard (`.pbix`) | Member 3 |
| KPI definitions | Member 3 |
| Architecture diagram | Member 4 |
| Three findings and recommendations | Member 4 + all |
| AI tool, prompt and comparison evidence | Member 4 |
| Final presentation | Member 4 + all |

A README should also explain the dataset source, extraction period, database setup, script execution order and how to open the Power BI dashboard.

---

## 8. Team Coordination Rules

To avoid last-minute integration problems, the following rules should be followed:

- Each member is responsible for delivering their assigned outputs on time.
- Every important deliverable must be reviewed by at least one other member.
- Database column names and KPI definitions must be agreed upon before dashboard implementation.
- All files must be stored in one shared project folder.
- SQL scripts must be organized and named clearly.
- The team should hold a short daily checkpoint to discuss completed work, blockers and upcoming dependencies.
- No member should wait until the final day to begin their contribution.
- Every member must understand the complete project, not only their assigned section.

---

## 9. Definition of Success

CivicPulse will be considered ready for presentation when:

1. A functional PostgreSQL database contains four related tables and a documented dataset.
2. SQL queries demonstrate meaningful data preparation and analytical capabilities.
3. Power BI presents accurate, interactive and clearly defined indicators.
4. At least three findings are supported by actual query results.
5. Recommendations follow logically from the findings.
6. The AI-generated dashboard comparison is documented and critically evaluated.
7. The presentation communicates the problem, solution, architecture, insights and benefits clearly.

**Final principle:** The strength of CivicPulse is not the number of charts or SQL queries it contains. Its strength is its ability to demonstrate how structured data, relational modeling and analytical SQL can help decision-makers understand public service performance and make better-informed decisions.

---

**CivicPulse — From Public Service Data to Actionable Insights.**