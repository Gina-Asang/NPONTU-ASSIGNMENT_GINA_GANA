"""
Npontu application Assignment: This is a Simple Health Check Service
Monitors 3 endpoints and exposes metrics via /health
"""

from flask import Flask, jsonify
import requests as r
import time as t
from datetime import datetime

app = Flask(__name__)

endpoints = [
    {"name": "Npontu Documentation", "url": "https://npontu.com/documentation/"},
    {"name": "Npontu Careers$Job", "url": "https://npontu.com/jobs-and-careers/"},
    {"name": "Ashesi University About", "url": "https://www.ashesi.edu.gh/about/"}
]

def check_endpoint(endpoint):                                  #function to check if an enpoint is responding
    result = {
        "name": endpoint["name"],  
        "url": endpoint["url"]    
    }
    
    start_time = t.time()                                    #gets current time
    
    try:
        response = r.get(endpoint["url"], timeout=5)         #should not take >5s to respond else timeout
        response_time = t.time() - start_time
        
        if 200 <= response.status_code < 300:
            result.update({
                "status": "UP",  
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "error": None
            })
        else:
            result.update({
                "status": "DOWN",  
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "error": f"HTTP error {response.status_code}"
            })
    
    except r.exceptions.Timeout:
        result.update({
            "status": "DOWN",  
            "status_code": 408,
            "response_time": None,
            "error": "Timeout after 5 seconds"
        })
    
    except r.exceptions.ConnectionError:
        result.update({
            "status": "DOWN",  
            "status_code": 503,
            "response_time": None,
            "error": "Connection failed"
        })
    
    except Exception as e:
        result.update({
            "status": "DOWN",  
            "status_code": 500,                               #any internal server error
            "response_time": None,
            "error": str(e)
        })
    
    return result

@app.route('/health')
def health():
    results = []
    up_count = 0
    total_response_time = 0
    
    for e in endpoints:  
        check_result = check_endpoint(e)  
        results.append(check_result)
        
        if check_result["status"] == "UP": 
            up_count += 1
            if check_result["response_time"]:
                total_response_time += check_result["response_time"]
    
    # Calculate the overall status
    if up_count == len(endpoints):                             #if all endpoints are working
        overall = "healthy"
    elif up_count == 0:                                        #if none is working
        overall = "down"
    else:                                       
        overall = "degraded"                                   #if some are working
    
    # average response time for UP endpoints
    avg_time = None              #first asuuming theres no response time
    if up_count > 0:
        avg_time = round(total_response_time / up_count, 3)
    
    response = {
       "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_status": overall,
        "summary": {
            "total_endpoints": len(endpoints),
            "up": up_count,
            "down": len(endpoints) - up_count
        },
        "endpoints": results
    }
    
    if avg_time:                                       # Add avg time if available
        response["summary"]["average_response_time_seconds"] = avg_time
    
    return jsonify(response)

if __name__ == '__main__':
    print("\nTo Access metrics at: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000)