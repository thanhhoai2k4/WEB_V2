import hashlib
import hmac
import urllib.parse


"""

    Doc: 


"""


class vnpay:
    requestData = {}
    responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        """
        Hàm này tạo ra URL đầy đủ để chuyển hướng người dùng sang VNPay.
        Nó sắp xếp các tham số, tạo chuỗi query, và tính toán mã băm (Secure Hash).
        """
        inputData = sorted(self.requestData.items())
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))
            
            # Dữ liệu để tính hash không được encode URL để đảm bảo tính nhất quán
            hasData = hasData + key + '=' + str(val) + '&'

        # Xóa ký tự & cuối cùng
        hasData = hasData[:-1]

        # Tạo mã băm Secure Hash (HMAC-SHA512)
        hashValue = self.__hmacsha512(secret_key, hasData)
        
        # URL cuối cùng = URL gốc + Tham số + Chữ ký bảo mật
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key):
        """
        Hàm này kiểm tra xem dữ liệu VNPay trả về có bị giả mạo không.
        """
        vnp_SecureHash = self.responseData.get('vnp_SecureHash')
        
        # Loại bỏ các tham số không tham gia vào việc tính hash
        if 'vnp_SecureHash' in self.responseData:
            del self.responseData['vnp_SecureHash']
        if 'vnp_SecureHashType' in self.responseData:
            del self.responseData['vnp_SecureHashType']

        inputData = sorted(self.responseData.items())
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                hasData = hasData + "&" + key + '=' + str(val)
            else:
                seq = 1
                hasData = key + '=' + str(val)
        
        hashValue = self.__hmacsha512(secret_key, hasData)
        
        # So sánh hash mình tính và hash VNPay gửi về
        return vnp_SecureHash == hashValue

    def __hmacsha512(self, key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()