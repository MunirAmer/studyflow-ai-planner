import pandas as pd


TASK_COLUMNS = [
    "ID",
    "Title",
    "Subject",
    "Deadline",
    "Priority",
    "Estimated Hours",
    "Status",
    "Notes",
    "Created At",
]


def validate_task_input(title, subject, estimated_hours):
    if not title.strip():
        return False, "Task title cannot be empty."

    if not subject.strip():
        return False, "Subject cannot be empty."

    if estimated_hours <= 0:
        return False, "Estimated hours must be greater than 0."

    return True, ""


def tasks_to_dataframe(tasks):
    df = pd.DataFrame(tasks, columns=TASK_COLUMNS)

    if not df.empty:
        df["Deadline"] = pd.to_datetime(df["Deadline"]).dt.date
        df["Created At"] = pd.to_datetime(df["Created At"])

    return df


def filter_and_sort_tasks(
    df,
    search_text,
    subject_filter,
    status_filter,
    priority_filter,
    deadline_range,
    sort_by,
    ascending,
):
    if df.empty:
        return df

    filtered_df = df.copy()

    if search_text.strip():
        search_text = search_text.lower().strip()

        search_mask = (
            filtered_df["Title"].str.lower().str.contains(search_text, na=False)
            | filtered_df["Subject"].str.lower().str.contains(search_text, na=False)
            | filtered_df["Notes"].str.lower().str.contains(search_text, na=False)
        )

        filtered_df = filtered_df[search_mask]

    if subject_filter != "All":
        filtered_df = filtered_df[filtered_df["Subject"] == subject_filter]

    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]

    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df["Priority"] == priority_filter]

    if deadline_range and len(deadline_range) == 2:
        start_date, end_date = deadline_range
        filtered_df = filtered_df[
            (filtered_df["Deadline"] >= start_date)
            & (filtered_df["Deadline"] <= end_date)
        ]

    if sort_by == "Priority":
        priority_order = {
            "High": 1,
            "Medium": 2,
            "Low": 3,
        }

        filtered_df["Priority Order"] = filtered_df["Priority"].map(priority_order)
        filtered_df = filtered_df.sort_values(
            by="Priority Order",
            ascending=ascending
        ).drop(columns=["Priority Order"])

    else:
        filtered_df = filtered_df.sort_values(
            by=sort_by,
            ascending=ascending
        )

    return filtered_df