"""
API routes for contour calculator.
"""
from flask import request, jsonify
from app.core.calculate import calculate


def register_api_routes(app):
    """Register calculation API routes to the Flask app"""
    
    @app.route('/api/calculate', methods=['POST'])
    def api_calculate():
        """
        Calculate contour parameters.
        
        Request JSON:
        {
            "config": {...},
            "input_data": {...}
        }
        
        Returns:
        {
            "n1": float,
            "n2": float,
            "n4": float,
            "angle_EF": float,
            "angle_D": float,
            "points": [[x, y], ...]
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            config = data.get("config", {})
            input_data = data.get("input_data", {})
            
            result = calculate(input_data, config)
            
            # Convert points to list of lists for JSON serialization
            result['points'] = [[x, y] for x, y in result['points']]
            
            return jsonify(result), 200
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Internal error: {str(e)}"}), 500
