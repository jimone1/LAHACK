#!/usr/bin/env python

# Copyright 2015 Google, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Draws squares around detected faces in the given image."""

import argparse

# [START vision_face_detection_tutorial_imports]
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
# [END vision_face_detection_tutorial_imports]

def detect_faces_Score(file):
    client = vision.ImageAnnotatorClient()

    image = vision.types.Image(content=file)

    response = client.face_detection(image=image)
    faces = response.face_annotations

    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')

    emotionScore = 0
    overAllScore = 0

    for face in faces:
        if likelihood_name[face.anger_likelihood] == 'UNKNOWN':
            emotionScore += 0
        elif likelihood_name[face.anger_likelihood] == 'VERY_UNLIKELY':
            emotionScore += 4
        elif likelihood_name[face.anger_likelihood] == 'UNLIKELY':
            emotionScore += 2
        elif likelihood_name[face.anger_likelihood] == 'POSSIBLE':
            emotionScore += 0
        elif likelihood_name[face.anger_likelihood] == 'LIKELY':
            emotionScore += -2
        elif likelihood_name[face.anger_likelihood] == 'VERY LIKELY':
            emotionScore += -4

        if likelihood_name[face.joy_likelihood] == 'UNKNOWN':
            emotionScore += 0
        elif likelihood_name[face.joy_likelihood] == 'VERY_UNLIKELY':
            emotionScore += -4
        elif likelihood_name[face.joy_likelihood] == 'UNLIKELY':
            emotionScore += -2
        elif likelihood_name[face.joy_likelihood] == 'POSSIBLE':
            emotionScore += 0
        elif likelihood_name[face.joy_likelihood] == 'LIKELY':
            emotionScore += 2
        elif likelihood_name[face.joy_likelihood] == 'VERY LIKELY':
            emotionScore += 4

        if likelihood_name[face.surprise_likelihood] == 'UNKNOWN':
            emotionScore += 0
        elif likelihood_name[face.surprise_likelihood] == 'VERY_UNLIKELY':
            emotionScore += -2
        elif likelihood_name[face.surprise_likelihood] == 'UNLIKELY':
            emotionScore += -1
        elif likelihood_name[face.surprise_likelihood] == 'POSSIBLE':
            emotionScore += 0
        elif likelihood_name[face.surprise_likelihood] == 'LIKELY':
            emotionScore += 1
        elif likelihood_name[face.surprise_likelihood] == 'VERY LIKELY':
            emotionScore += 2

    if emotionScore == 0:
        overAllScore += 1
    elif emotionScore < 0 and emotionScore > -8:
        overAllScore += -3
    elif emotionScore < -8:
        overAllScore += -4
    elif emotionScore > 0 and emotionScore < 8:
        overAllScore += 2
    elif emotionScore > 8:
        overAllScore += 3

    if overAllScore == 2:
        return "FAIR"
    elif overAllScore < 2:
        return "BAD"
    else: return "GOOD"

# [START vision_face_detection_tutorial_send_request]
def detect_face(image, max_results=4):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of Face objects with information about the picture.
    """
    # [START vision_face_detection_tutorial_client]
    client = vision.ImageAnnotatorClient()
    # [END vision_face_detection_tutorial_client]

    image = types.Image(content=image)

    return client.face_detection(image=image, max_results=max_results).face_annotations
# [END vision_face_detection_tutorial_send_request]


# [START vision_face_detection_tutorial_process_response]
def highlight_faces(image, faces, output_filename):
    """Draws a polygon around the faces, then saves to output_filename.

    Args:
      image: a file containing the image with the faces.
      faces: a list of faces found in the file. This should be in the format
          returned by the Vision API.
      output_filename: the name of the image file to be created, where the
          faces have polygons drawn around them.
    """
    im = Image.open(image)
    draw = ImageDraw.Draw(im)
    # Sepecify the font-family and the font-size
    for face in faces:
        box = [(vertex.x, vertex.y)
               for vertex in face.bounding_poly.vertices]
        draw.line(box + [box[0]], width=5, fill='#00ff00')
        # Place the confidence value/score of the detected faces above the
        # detection box in the output image
        draw.text(((face.bounding_poly.vertices)[0].x,
                   (face.bounding_poly.vertices)[0].y - 30),
                  str(format(face.detection_confidence, '.3f')) + '%',
                  fill='#FF0000')
    im.save(output_filename)
# [END vision_face_detection_tutorial_process_response]


# [START vision_face_detection_tutorial_run_application]
def main(input_filename, output_filename, max_results):
    with open(input_filename, 'rb') as image:
        faces = detect_face(image, max_results)
        print('Found {} face{}'.format(
            len(faces), '' if len(faces) == 1 else 's'))

        print('Writing to file {}'.format(output_filename))
        # Reset the file pointer, so we can read the file again
        image.seek(0)
        highlight_faces(image, faces, output_filename)
# [END vision_face_detection_tutorial_run_application]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Detects faces in the given image.')
    parser.add_argument(
        'input_image', help='the image you\'d like to detect faces in.')
    parser.add_argument(
        '--out', dest='output', default='out.jpg',
        help='the name of the output file.')
    parser.add_argument(
        '--max-results', dest='max_results', default=4,
        help='the max results of face detection.')
    args = parser.parse_args()

    main(args.input_image, args.output, args.max_results)
