import numpy as np

def get_face_distance(face, facesize_1m, inf=9999):
  
  # Detect none
  if face is None:
    return inf
  
  # Face too small
  w, h, _ = face.shape
  face_size = w * h
  if face_size == 0:
    return inf
  
  # Calculate distance: distance is inversely proportional to square root of face size
  distance = np.sqrt(facesize_1m / face_size)
  
  return distance

def in_active_range(face, active_range, facesize_1m, precise=1):
  distance = round(get_face_distance(face, facesize_1m), precise)
  return distance, distance <= active_range
  
  
  
  