import numpy as np

def extract_keypoints_features(keypoints):
  """
    Extracts features from a set of keypoints representing human body joints.

    Parameters:
    - keypoints (numpy array): Array containing the coordinates of human body keypoints.

    Returns:
    - features (numpy array): Array containing the extracted features, including distances and angles.
    """
  
  features = []

  def distance(p1, p2):
        """
        Calculates the Euclidean distance between two points.

        Parameters:
        - p1 (numpy array): Coordinates of point 1.
        - p2 (numpy array): Coordinates of point 2.

        Returns:
        - dist (float): Euclidean distance between the points.
        """
        return np.linalg.norm(p1 - p2)

  def angle(p1, p2, p3):
      """
        Calculates the angle between three points using the arctangent function.

        Parameters:
        - p1 (numpy array): Coordinates of the first point.
        - p2 (numpy array): Coordinates of the vertex point.
        - p3 (numpy array): Coordinates of the third point.

        Returns:
        - ang (float): Angle between the vectors formed by the points, in radians.
        """
      a = p1 - p2
      b = p3 - p2
      return np.arctan2(b[1], b[0]) - np.arctan2(a[1], a[0])

  # Main features (distance & angle)
  shoulder_distance = distance(keypoints[5, :2], keypoints[6, :2])
  hip_distance = distance(keypoints[11, :2], keypoints[12, :2])
  shoulder_hip_distance = distance(keypoints[5, :2], keypoints[11, :2])
  shoulder_spine_angle = angle(keypoints[5, :2], keypoints[11, :2], keypoints[6, :2])

  # Additional distances
  elbow_wrist_distance = distance(keypoints[7, :2], keypoints[9, :2])  # Elbow to wrist
  shoulder_waist_distance = distance(keypoints[5, :2], keypoints[11, :2])  # Shoulder to waist
  hip_ankle_distance = distance(keypoints[11, :2], keypoints[15, :2])  # Hip to ankle

  # Additional angles
  elbow_wrist_shoulder_angle = angle(keypoints[7, :2], keypoints[9, :2], keypoints[5, :2])  # Elbow-wrist-shoulder
  shoulder_hip_knee_angle = angle(keypoints[5, :2], keypoints[11, :2], keypoints[13, :2])  # Shoulder-hip-knee

  features.extend([
      shoulder_distance, hip_distance, shoulder_hip_distance, shoulder_spine_angle,
      elbow_wrist_distance, shoulder_waist_distance, hip_ankle_distance,
      elbow_wrist_shoulder_angle, shoulder_hip_knee_angle
  ])

  return np.array(features)


def preprocess_keypoints(keypoints):
    """
    Normalizes and preprocesses keypoints to extract relevant features for prediction.

    Parameters:
    - keypoints (numpy array): Array containing the coordinates of human body keypoints.

    Returns:
    - features (numpy array): Array containing the extracted features, reshaped for prediction.
    """
    
    # Normalize the keypoints
    keypoints = keypoints / np.max(keypoints)

    # Preprocess the keypoints to extract features
    features = extract_keypoints_features(keypoints)

    # Reshape the features for prediction
    features = features.reshape(1, -1)

    return features


def load_categories(file_path):
    """
    Loads a list of categories from a specified text file.

    Parameters:
    - file_path (str): Path to the text file containing category names.

    Returns:
    - categories (list of str): List of categories.
    """
    with open(file_path, 'r') as file:
        categories = [line.strip() for line in file]
    return categories