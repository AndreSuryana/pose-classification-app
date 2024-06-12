# CNN Pose Classification Application

This Flask application utilizes a Convolutional Neural Network (CNN) model to predict keypoints of a person's body and classify them into different posture categories. It also provides functionalities for storing and retrieving prediction history in a SQLite database.


## Prerequisites

- Python 3.x installed on the system
- Virtual environment (optional, but recommended)


## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/AndreSuryana/pose-classification-api.git
    cd pose-classification-api
    ```

2. **Create and activate a virtual environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```


### Configuration




### Running the Application

1. **Start the Flask application:**
    ```bash
    python3 app.py
    ```
    or
    ```bash
    flask run
    ```


## Example API Requests

Once the application is running, access using cURL or API Client (e.g., [Insomnia](https://insomnia.rest/), [Postman](https://www.postman.com/)) on `http://localhost:5000`

- **Predict Keypoints**<br>
    Endpoint to predict keypoints of a person's body based on input keypoints data.
    ```curl
    curl --request POST \
    --url http://127.0.0.1:5000/predict \
    --header 'Content-Type: application/json' \
    --data '{
        "keypoints": [
            [0.15548649, 0.5229879,  0.65571499],
            [0.13679968, 0.51310277, 0.62321991],
            [0.13609274, 0.51227981, 0.72100508],
            [0.1417376,  0.46356499, 0.64876258],
            [0.14317547, 0.46341836, 0.84622955],
            [0.22421542, 0.44037327, 0.77974123],
            [0.22518402, 0.45176178, 0.72984433],
            [0.3575961,  0.53775316, 0.58973157],
            [0.36001056, 0.55181772, 0.63526499],
            [0.33267716, 0.53916985, 0.30891362],
            [0.32318941, 0.54232681, 0.34550923],
            [0.49347052, 0.46195826, 0.68969256],
            [0.49969825, 0.45843035, 0.71252894],
            [0.69683152, 0.45270997, 0.7548725],
            [0.70242524, 0.44874549, 0.72100139],
            [0.87305951, 0.44998547, 0.58023518],
            [0.90624917, 0.43075335, 0.81421185]
        ]
    }
    ```

- **Load Prediction History**<br>
    Endpoint to load the prediction history from the database.
    ```curl
    curl --request GET \
    --url http://localhost:5000/history
    ```


## How to Update the CNN Model

1. Copy the stored model `.keras` file into `cnn/` folder
2. Copy the `categories.txt` file into `cnn/` folder. Categories are separated by new-line.


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## License

[MIT](LICENSE)