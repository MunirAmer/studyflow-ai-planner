import streamlit as st
from database import create_tasks_table, add_task, get_all_tasks, update_task_status, delete_task
from utils import validate_task_input, tasks_to_dataframe, filter_and_sort_tasks
from analytics import (
    get_summary_metrics,
    create_status_chart,
    create_priority_chart,
    create_hours_by_subject_chart,
    create_workload_by_deadline_chart,
    create_completion_by_subject_chart,
    get_deadline_insights,
)
from ai_helper import generate_rule_based_advice, generate_ai_study_plan

st.set_page_config(
    page_title="StudyFlow",
    page_icon="📚",
    layout="wide"
)


create_tasks_table()


st.title("📚 StudyFlow")
st.subheader("AI-Powered Study Planner and Learning Analytics Dashboard")


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Add Task", "Manage Tasks", "Analytics", "AI Advisor"])


with tab1:
    st.header("Dashboard")

    tasks = get_all_tasks()
    df = tasks_to_dataframe(tasks)

    if df.empty:
        st.info("No study tasks yet. Add your first task from the Add Task page.")
    else:
        total_tasks = len(df)
        completed_tasks = len(df[df["Status"] == "Completed"])
        pending_tasks = total_tasks - completed_tasks
        completion_rate = round((completed_tasks / total_tasks) * 100, 1)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Tasks", total_tasks)
        col2.metric("Completed", completed_tasks)
        col3.metric("Pending", pending_tasks)
        col4.metric("Completion Rate", f"{completion_rate}%")

        st.write("Recent Study Tasks")
        st.dataframe(df, use_container_width=True)


with tab2:
    st.header("Add a New Study Task")

    with st.form("add_task_form"):
        title = st.text_input("Task Title")
        subject = st.text_input("Subject")
        deadline = st.date_input("Deadline")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        estimated_hours = st.number_input(
            "Estimated Study Hours",
            min_value=0.0,
            step=0.5
        )
        status = st.selectbox(
            "Status",
            ["Not Started", "In Progress", "Completed"]
        )
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Save Task")

        if submitted:
            is_valid, error_message = validate_task_input(
                title,
                subject,
                estimated_hours
            )

            if not is_valid:
                st.error(error_message)
            else:
                add_task(
                    title=title.strip(),
                    subject=subject.strip(),
                    deadline=str(deadline),
                    priority=priority,
                    estimated_hours=estimated_hours,
                    status=status,
                    notes=notes.strip()
                )

                st.success("Task saved successfully.")


with tab3:
    st.header("Manage Study Tasks")

    tasks = get_all_tasks()
    df = tasks_to_dataframe(tasks)

    if df.empty:
        st.info("No tasks found.")
    else:
        st.subheader("Search, Filter, and Sort")

        search_text = st.text_input(
            "Search",
            placeholder="Search by title, subject, or notes"
        )

        subject_options = ["All"] + sorted(df["Subject"].dropna().unique().tolist())

        col1, col2, col3 = st.columns(3)

        with col1:
            subject_filter = st.selectbox("Subject", subject_options)

        with col2:
            status_filter = st.selectbox(
                "Status",
                ["All", "Not Started", "In Progress", "Completed"]
            )

        with col3:
            priority_filter = st.selectbox(
                "Priority",
                ["All", "High", "Medium", "Low"]
            )

        min_deadline = df["Deadline"].min()
        max_deadline = df["Deadline"].max()

        deadline_range = st.date_input(
            "Deadline Range",
            value=(min_deadline, max_deadline)
        )

        col4, col5 = st.columns(2)

        with col4:
            sort_by = st.selectbox(
                "Sort By",
                [
                    "Deadline",
                    "Priority",
                    "Estimated Hours",
                    "Created At",
                    "Title",
                    "Subject",
                    "Status",
                ]
            )

        with col5:
            sort_direction = st.selectbox(
                "Sort Direction",
                ["Ascending", "Descending"]
            )

        ascending = sort_direction == "Ascending"

        filtered_df = filter_and_sort_tasks(
            df=df,
            search_text=search_text,
            subject_filter=subject_filter,
            status_filter=status_filter,
            priority_filter=priority_filter,
            deadline_range=deadline_range,
            sort_by=sort_by,
            ascending=ascending,
        )

        st.write(f"Showing {len(filtered_df)} of {len(df)} tasks")

        st.dataframe(filtered_df, use_container_width=True)

        st.divider()

        if filtered_df.empty:
            st.warning("No tasks match the current filters.")
        else:
            task_ids = filtered_df["ID"].tolist()
            task_lookup = filtered_df.set_index("ID").to_dict("index")

            st.subheader("Update Task Status")

            selected_task_id = st.selectbox(
                "Choose a task to update",
                task_ids,
                format_func=lambda task_id: (
                    f"{task_lookup[task_id]['Title']} - "
                    f"{task_lookup[task_id]['Subject']} "
                    f"({task_lookup[task_id]['Status']})"
                ),
                key="update_task_selectbox"
            )

            current_status = task_lookup[selected_task_id]["Status"]

            status_options = ["Not Started", "In Progress", "Completed"]

            new_status = st.selectbox(
                "New Status",
                status_options,
                index=status_options.index(current_status),
                key="new_status_selectbox"
            )

            if st.button("Update Status"):
                update_task_status(selected_task_id, new_status)
                st.success("Task status updated successfully.")
                st.rerun()

            st.divider()

            st.subheader("Delete Task")

            delete_task_id = st.selectbox(
                "Choose a task to delete",
                task_ids,
                format_func=lambda task_id: (
                    f"{task_lookup[task_id]['Title']} - "
                    f"{task_lookup[task_id]['Subject']} "
                    f"({task_lookup[task_id]['Status']})"
                ),
                key="delete_task_selectbox"
            )

            confirm_delete = st.checkbox(
                "I understand that this task will be permanently deleted.",
                key="confirm_delete_checkbox"
            )

            if st.button("Delete Task"):
                if not confirm_delete:
                    st.warning("Please confirm before deleting the task.")
                else:
                    delete_task(delete_task_id)
                    st.success("Task deleted successfully.")
                    st.rerun()


with tab4:
    st.header("Learning Analytics Dashboard")

    tasks = get_all_tasks()
    df = tasks_to_dataframe(tasks)

    if df.empty:
        st.info("No data available yet. Add study tasks to view analytics.")
    else:
        metrics = get_summary_metrics(df)
        insights = get_deadline_insights(df)

        st.subheader("Study Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Tasks", metrics["total_tasks"])
        col2.metric("Completed Tasks", metrics["completed_tasks"])
        col3.metric("Pending Tasks", metrics["pending_tasks"])

        col4, col5, col6 = st.columns(3)

        col4.metric("Completion Rate", f"{metrics['completion_rate']}%")
        col5.metric("Total Study Hours", round(metrics["total_hours"], 1))
        col6.metric("High Priority Pending", metrics["high_priority_tasks"])

        st.divider()

        st.subheader("Deadline Insights")

        col7, col8, col9 = st.columns(3)

        col7.metric("Overdue Tasks", insights["overdue_tasks"])
        col8.metric("Due in Next 7 Days", insights["due_soon_tasks"])

        if insights["next_deadline"] is None:
            col9.metric("Next Deadline", "None")
        else:
            col9.metric("Next Deadline", str(insights["next_deadline"]))

        st.divider()

        st.subheader("Visual Analysis")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            status_chart = create_status_chart(df)
            st.pyplot(status_chart)

        with chart_col2:
            priority_chart = create_priority_chart(df)
            st.pyplot(priority_chart)

        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            hours_chart = create_hours_by_subject_chart(df)
            st.pyplot(hours_chart)

        with chart_col4:
            completion_chart = create_completion_by_subject_chart(df)
            st.pyplot(completion_chart)

        workload_chart = create_workload_by_deadline_chart(df)

        if workload_chart is not None:
            st.pyplot(workload_chart)
        else:
            st.success("All tasks are completed. No upcoming workload to display.")

        st.divider()

        st.subheader("Data Science Summary")

        strongest_subject = (
            df.groupby("Subject")["Estimated Hours"]
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )

        st.write(
            f"""
            Based on the current task data, the subject with the highest estimated
            workload is **{strongest_subject}**. The overall completion rate is
            **{metrics['completion_rate']}%**, with **{metrics['pending_tasks']}**
            tasks still pending. This dashboard helps the student understand where
            their study time is going and which deadlines need attention.
            """
        )

with tab5:
    st.header("AI Study Advisor")

    tasks = get_all_tasks()
    df = tasks_to_dataframe(tasks)

    if df.empty:
        st.info("Add study tasks first to receive AI-powered study advice.")
    else:
        st.write(
            """
            The AI Study Advisor analyzes your current tasks, deadlines, priorities,
            and estimated study hours to suggest what you should focus on next.
            """
        )

        st.subheader("Smart Recommendation")

        rule_based_advice = generate_rule_based_advice(df)
        st.info(rule_based_advice)

        st.divider()

        st.subheader("AI-Generated Study Plan")

        use_ai = st.checkbox("Use OpenAI to generate a personalized study plan")

        if use_ai:
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
            except Exception:
                api_key = None

            if not api_key:
                st.error(
                    "OpenAI API key was not found. Add it to .streamlit/secrets.toml."
                )
            else:
                if st.button("Generate AI Study Plan"):
                    with st.spinner("Generating your study plan..."):
                        ai_plan = generate_ai_study_plan(df, api_key)
                        st.write(ai_plan)