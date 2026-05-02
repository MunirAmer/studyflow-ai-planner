import matplotlib.pyplot as plt
from datetime import date, timedelta


def get_summary_metrics(df):
    if df.empty:
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_rate": 0,
            "total_hours": 0,
            "high_priority_tasks": 0,
        }

    total_tasks = len(df)
    completed_tasks = len(df[df["Status"] == "Completed"])
    pending_tasks = total_tasks - completed_tasks
    total_hours = df["Estimated Hours"].sum()

    high_priority_tasks = len(
        df[(df["Priority"] == "High") & (df["Status"] != "Completed")]
    )

    completion_rate = round((completed_tasks / total_tasks) * 100, 1)

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": completion_rate,
        "total_hours": total_hours,
        "high_priority_tasks": high_priority_tasks,
    }


def create_status_chart(df):
    status_data = df["Status"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(status_data.index, status_data.values)

    ax.set_title("Tasks by Status")
    ax.set_xlabel("Status")
    ax.set_ylabel("Number of Tasks")

    for index, value in enumerate(status_data.values):
        ax.text(index, value, str(value), ha="center", va="bottom")

    plt.tight_layout()
    return fig


def create_priority_chart(df):
    priority_data = df["Priority"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(
        priority_data.values,
        labels=priority_data.index,
        autopct="%1.1f%%",
        startangle=90,
    )

    ax.set_title("Task Priority Distribution")
    plt.tight_layout()
    return fig


def create_hours_by_subject_chart(df):
    subject_data = (
        df.groupby("Subject")["Estimated Hours"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(subject_data.index, subject_data.values)

    ax.set_title("Estimated Study Hours by Subject")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Estimated Study Hours")
    ax.tick_params(axis="x", rotation=30)

    for index, value in enumerate(subject_data.values):
        ax.text(index, value, str(round(value, 1)), ha="center", va="bottom")

    plt.tight_layout()
    return fig


def create_workload_by_deadline_chart(df):
    incomplete_df = df[df["Status"] != "Completed"].copy()

    if incomplete_df.empty:
        return None

    workload_data = (
        incomplete_df.groupby("Deadline")["Estimated Hours"]
        .sum()
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(workload_data.index, workload_data.values, marker="o")

    ax.set_title("Upcoming Workload by Deadline")
    ax.set_xlabel("Deadline")
    ax.set_ylabel("Estimated Study Hours")
    ax.tick_params(axis="x", rotation=30)

    plt.tight_layout()
    return fig


def create_completion_by_subject_chart(df):
    subject_summary = (
        df.groupby("Subject")
        .agg(
            Total_Tasks=("ID", "count"),
            Completed_Tasks=("Status", lambda x: (x == "Completed").sum()),
        )
    )

    subject_summary["Completion Rate"] = round(
        (subject_summary["Completed_Tasks"] / subject_summary["Total_Tasks"]) * 100,
        1,
    )

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(subject_summary.index, subject_summary["Completion Rate"])

    ax.set_title("Completion Rate by Subject")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Completion Rate (%)")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=30)

    for index, value in enumerate(subject_summary["Completion Rate"]):
        ax.text(index, value, f"{value}%", ha="center", va="bottom")

    plt.tight_layout()
    return fig


def get_deadline_insights(df):
    if df.empty:
        return {
            "overdue_tasks": 0,
            "due_soon_tasks": 0,
            "next_deadline": None,
        }

    today = date.today()
    next_week = today + timedelta(days=7)

    incomplete_df = df[df["Status"] != "Completed"].copy()

    if incomplete_df.empty:
        return {
            "overdue_tasks": 0,
            "due_soon_tasks": 0,
            "next_deadline": None,
        }

    overdue_tasks = len(incomplete_df[incomplete_df["Deadline"] < today])

    due_soon_tasks = len(
        incomplete_df[
            (incomplete_df["Deadline"] >= today)
            & (incomplete_df["Deadline"] <= next_week)
        ]
    )

    next_deadline = incomplete_df["Deadline"].min()

    return {
        "overdue_tasks": overdue_tasks,
        "due_soon_tasks": due_soon_tasks,
        "next_deadline": next_deadline,
    }