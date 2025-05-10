from label_studio_sdk.client import LabelStudio

LABEL_STUDIO_URL = 'http://192.5.87.42:8090'  # Change if needed
API_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA1NDExNjY0OSwiaWF0IjoxNzQ2OTE2NjQ5LCJqdGkiOiIyNTUwMjE0M2RkYzA0YzE1YWZlOTAwZGY4YjViOGY1NCIsInVzZXJfaWQiOjF9.Yqx9lGOn7ROF5ANU5YUoZYACuyvzJT-0m8bS1kcSX4Q'  # Paste your token from Access Tokens page

def main():
    # Connect to Label Studio
    ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_TOKEN)
    print("Connected to Label Studio.")

    # List projects
    projects = list(ls.projects.list())
    print(f"Found {len(projects)} project(s).")
    for p in projects:
        print(f" - {p.id}: {p.title}")

    # Use XML string for label config
    label_config = '''
    <View>
      <Header value="Question:"/>
      <Text name="question" value="$question"/>
      <Header value="Model Answer:"/>
      <Text name="answer" value="$answer"/>
      <Header value="Rating:"/>
      <Choices name="rating" toName="answer" choice="single" showInLine="true">
        <Choice value="Excellent"/>
        <Choice value="Good"/>
        <Choice value="Average"/>
        <Choice value="Poor"/>
        <Choice value="Incorrect"/>
      </Choices>
      <TextArea name="feedback" toName="answer" placeholder="Provide feedback on the answer..." rows="4"/>
    </View>
    '''

    try:
        project = ls.projects.create(
            title='SDK Test Project',
            label_config=label_config,
            description='A test project created by the SDK test script'
        )
        print(f"Project created! ID: {project.id}, Title: {project.title}")
    except Exception as e:
        print(f"Error creating project: {e}")

if __name__ == "__main__":
    main()