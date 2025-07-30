"""
QR Code utilities for equipment management
Handles QR code generation and data encoding/decoding
"""

import qrcode
import qrcode.constants
import json
import base64
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class QRCodeGenerator:
    """Generate QR codes for equipment"""
    
    def __init__(self):
        self.base_url = "https://church-inventory.replit.app"  # Update with your domain
        
    def generate_equipment_qr_data(self, equipment_id, equipment_name, category):
        """Generate QR code data for equipment"""
        qr_data = {
            "type": "equipment",
            "id": equipment_id,
            "name": equipment_name,
            "category": category,
            "url": f"{self.base_url}/equipment/{equipment_id}",
            "scan_url": f"{self.base_url}/scan/{equipment_id}"
        }
        return json.dumps(qr_data)
    
    def generate_qr_code_image(self, data, size=(300, 300)):
        """Generate QR code image"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Resize if needed
            if size != img.size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            return img
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            return None
    
    def generate_qr_code_base64(self, data, size=(300, 300)):
        """Generate QR code as base64 string for embedding in HTML"""
        img = self.generate_qr_code_image(data, size)
        if not img:
            return None
        
        try:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            logger.error(f"Error converting QR code to base64: {str(e)}")
            return None
    
    def generate_equipment_qr_base64(self, equipment_id, equipment_name, category, size=(300, 300)):
        """Generate equipment QR code as base64 string"""
        qr_data = self.generate_equipment_qr_data(equipment_id, equipment_name, category)
        return self.generate_qr_code_base64(qr_data, size)

class QRCodeScanner:
    """Handle QR code scanning and data parsing"""
    
    @staticmethod
    def parse_qr_data(qr_text):
        """Parse QR code text and extract equipment information"""
        try:
            # Try to parse as JSON first
            data = json.loads(qr_text)
            if data.get("type") == "equipment":
                return {
                    "success": True,
                    "equipment_id": data.get("id"),
                    "equipment_name": data.get("name"),
                    "category": data.get("category"),
                    "scan_url": data.get("scan_url"),
                    "data_type": "json"
                }
        except json.JSONDecodeError:
            pass
        
        # Try to parse as URL
        if qr_text.startswith("http"):
            # Extract equipment ID from URL patterns
            if "/equipment/" in qr_text:
                try:
                    equipment_id = qr_text.split("/equipment/")[-1].split("?")[0].split("/")[0]
                    return {
                        "success": True,
                        "equipment_id": int(equipment_id),
                        "data_type": "url",
                        "url": qr_text
                    }
                except (ValueError, IndexError):
                    pass
            elif "/scan/" in qr_text:
                try:
                    equipment_id = qr_text.split("/scan/")[-1].split("?")[0].split("/")[0]
                    return {
                        "success": True,
                        "equipment_id": int(equipment_id),
                        "data_type": "scan_url",
                        "url": qr_text
                    }
                except (ValueError, IndexError):
                    pass
        
        # Try to parse as plain equipment ID
        try:
            equipment_id = int(qr_text.strip())
            return {
                "success": True,
                "equipment_id": equipment_id,
                "data_type": "id"
            }
        except ValueError:
            pass
        
        return {
            "success": False,
            "error": "Unable to parse QR code data",
            "raw_data": qr_text
        }

# Global instances
qr_generator = QRCodeGenerator()
qr_scanner = QRCodeScanner()