from openai import OpenAI


def prepare_task_summary(df):
    if df.empty:
        return "There are no study tasks yet."

    task_lines = []

    for _, row in df.iterrows():
        task_lines.append(
            f"- Title: {row['Title']}; "
            f"Subject: {row['Subject']}; "
            f"Deadline: {row['Deadline']}; "
            f"Priority: {row['Priority']}; "
            f"Estimated Hours: {row['Estimated Hours']}; "
            f"Status: {row['Status']}; "
            f"Notes: {row['Notes']}"
        )

    return "\n".join(task_lines)


def generate_rule_based_advice(df):
    if df.empty:
        return "Add a few study tasks first, then the advisor can analyze your workload."

    incomplete_df = df[df["Status"] != "Completed"].copy()

    if incomplete_df.empty:
        return "All tasks are completed. Good work. You can use this time to review older material or prepare for upcoming topics."

    high_priority = incomplete_df[incomplete_df["Priority"] == "High"]
    nearest_deadline = incomplete_df.sort_values(by="Deadline").iloc[0]

    subject_hours = (
        incomplete_df.groupby("Subject")["Estimated Hours"]
        .sum()
        .sort_values(ascending=False)
    )

    heaviest_subject = subject_hours.index[0]
    heaviest_hours = subject_hours.iloc[0]

    advice = f"""
    Quick recommendation:

    Start with **{nearest_deadline['Title']}** because it has the nearest deadline.

    Your heaviest subject right now is **{heaviest_subject}**, with about **{heaviest_hours}** estimated study hours remaining.

    You currently have **{len(high_priority)}** high-priority incomplete task(s).

    Suggested plan:
    1. Finish the nearest deadline first.
    2. Spend extra time on {heaviest_subject}.
    3. Break large tasks into smaller sessions.
    4. Mark tasks as completed once finished so the dashboard stays accurate.
    """

    return advice


def generate_ai_study_plan(df, api_key):
    if df.empty:
        return "Add study tasks first so the AI advisor can create a useful plan."

    task_summary = prepare_task_summary(df)

    prompt = f"""
    You are an academic study planning assistant.

    The user is a student using a study planner app. Analyze the task list below and create a practical study plan.

    Requirements:
    - Prioritize urgent and high-priority incomplete tasks.
    - Mention which task should be done first.
    - Mention which subject needs the most attention.
    - Give a short 2-3 day study plan.
    - Keep the language clear and encouraging.
    - Do not invent tasks that are not listed.
    - If a task is already completed, do not prioritize it.

    Student task data:
    {task_summary}
    """

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-5.4-mini",
            input=prompt,
        )

        return response.output_text

    except Exception as error:
        return f"AI advisor error: {error}"