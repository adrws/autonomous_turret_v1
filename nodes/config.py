# Zenoh keys
camera_centering_data = "camera_centering/data"
camera_centering_commands = "camera_centering/commands"
camera_centering_feedback = "camera_centering/feedback"
kinematics_data = "kinematics/data"
kinematics_commands = "kinematics/commands"
keyboard_controls = "keyboard_controls"

# Turret Parameters
deadzone = 30

# Long strings
data_collection_message = "\nData Collection: " \
"\n - You have manual control over the turret using keyboard controls. " \
"\n - Line up a shot that lands in the bounding box, if the shot is correct then add it to the dataset." \
"\n - Make sure all features are correct before adding them to the dataset."
training_message = "\nTraining: " \
"\n - The model will make a prediction based on its initial dataset." \
"\n - If the prediction is incorrect, then you can manually control the turret and add the correct shot to the dataset." \
"\n - After every 10 corrections it will be appended to the main database and the model will be retrained on the data." \
"\n - Training will likely take place until the model's accuracy is ~ 0.9."
autonomous_message = "\nAutonomous: " \
"\n - The model will automatically make predictions, no manual interventions necessary."