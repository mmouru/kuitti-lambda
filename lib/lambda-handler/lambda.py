import boto3
import json
import datetime
import uuid
import base64
import cv2
import numpy as np

def main(event, context):

    s3 = boto3.client('s3')
    bucket_name = "kuittiprojektistack-kuittibucket47c27659-19ii9u03nrnse"

    try:
        response = s3.get_object(Bucket=bucket_name, Key="test1.png")
        image_data = response['Body'].read()
    except:
        print("errors")

    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    ret, th1 = cv2.threshold(gray, 160,255, cv2.THRESH_BINARY)

    kernel = np.ones((10,10), np.uint8)
    opening = cv2.morphologyEx(th1, cv2.MORPH_OPEN, kernel)
    closing_kernel = np.ones((100, 100), np.uint8)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, closing_kernel)
    edges = cv2.Canny(closing, 50, 100)

    bitwise_map = np.where(closing != 0, 1, closing)
    filtered_image = bitwise_map * th1

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
    maxContour = contours[0]

    paper_contour = cv2.approxPolyDP(maxContour, 0.04 * cv2.arcLength(maxContour, True), True)

    paper_contour_reshaped = paper_contour.reshape(4,2)
    rect = cv2.minAreaRect(paper_contour_reshaped)
    box = cv2.boxPoints(rect)
    box = np.intp(box)

    output_rect = np.array([])
    og_height = gray.shape[0]
    og_width = gray.shape[1]
    box_height = np.abs(box[2][1]- box[1][1])
    box_width = np.abs(box[1][0] - box[0][0])
    aspect_ratio = box_height / box_width

    output_width = og_width
    output_height = int(aspect_ratio * og_height)
    output_rect = np.array([[0, 0], [output_width - 1, 0], [output_width - 1, output_height - 1], [0, output_height - 1]], dtype=np.float32)
    transformation_matrix = cv2.getPerspectiveTransform(box.astype(np.float32), output_rect)
    output_image = cv2.warpPerspective(filtered_image, transformation_matrix,(output_width, output_height))



    
    file_name = str(uuid.uuid4())[:36] + ".jpg"

    # Get current time
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
    
    s3.put_object(Body=output_image, Bucket=bucket_name, Key=file_name, ContentType='image/jpeg')
    return {
        'statusCode': 200,
        'data': 'Image saved to bucket: ' + bucket_name,
        'timestamp': formatted_datetime 
    }