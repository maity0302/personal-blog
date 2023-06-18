from datetime import date, datetime, timedelta
from io import BytesIO
from .models import User
from django.db.models import Q
import re
from PIL import Image


def loginValidate(emailOrUsername, password, message=None):
    try:
        user = User.objects.get(Q(username=emailOrUsername) | Q(
            email=emailOrUsername), password=password)
        if user:
            return {'user': user, 'success': True, 'message': 'Đăng nhập thành công.'}
        else:
            return {'user': None, 'success': False, 'message': 'Thông tin đăng nhập không chính xác.'}
    except User.DoesNotExist:
        return {'user': None, 'success': False, 'message': 'Invalid credentials'}
    except Exception as e:
        # handle database connection errors or other exceptions
        return {'user': None, 'success': False, 'message': e or 'Đã có lỗi xảy ra. Vui lòng thử lại sau.'}


def registerValidate(firstname, lastname, username, email, password, password_confirm, birthday_day, birthday_month, birthday_year):
    if not (firstname or lastname or username or email or password or password_confirm or birthday_day or birthday_month or birthday_year):
        return {'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin.'}

    try:
        User.objects.get(username=username)
        return {'success': False, 'message': 'Tên đăng nhập đã tồn tại.'}
    except User.DoesNotExist:
        pass
    except Exception as e:
        return {'success': False, 'message': 'Đã có lỗi xảy ra. Vui lòng thử lại sau.'}

    try:
        User.objects.get(email=email)
        return {'success': False, 'message': 'Email đã tồn tại.'}
    except User.DoesNotExist:
        pass
    except Exception as e:
        return {'success': False, 'message': 'Đã có lỗi xảy ra. Vui lòng thử lại sau.'}

    if 6 < len(firstname) <= 20 and firstname.isalpha():
        return {'success': False, 'message': 'Họ phải có từ 2 - 20 ký tự, không chứa số, ký tự đặc biệt.'}

    if 6 < len(lastname) <= 20 and lastname.isalpha():
        return {'success': False, 'message': 'Tên phải có từ 2 - 20 ký tự, không chứa số, ký tự đặc biệt.'}

    if 6 < len(username) <= 20 and username.isalnum():
        return {'success': False, 'message': 'Tên đăng nhập phải có từ 2 - 20 ký tự, không chứa ký tự đặc biệt.'}

    if password != password_confirm:
        return {'success': False, 'message': 'Mật khẩu không khớp.'}

    """
    Check password:
        - At least 1 digit
        - At least 1 uppercase character
        - At least 1 lowercase character
        - At least 1 special character
        - Minimum 8 characters
        - Maximum 36 characters
    """

    if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z])(?=.*[!@#$%^&*()_+}{:;\'?/.,<>])(?!.*\s).{8,36}$', password):
        return {'success': False, 'message': 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt.'}

    if birthday_day < 1 or birthday_day > 31:
        return {'success': False, 'message': 'Ngày sinh không hợp lệ.'}

    if birthday_month < 1 or birthday_month > 12:
        return {'success': False, 'message': 'Tháng sinh không hợp lệ.'}

    if datetime.now().year - birthday_year < 10:
        return {'success': False, 'message': 'Bạn chưa đủ tuổi để đăng ký tài khoản.'}
    return {'success': True, 'message': 'Đăng ký thành công.'}


def editProfileValidate(firstname, lastname, username, currentUsername, email, currentEmail, birthday_day, birthday_month, birthday_year):

    if not (firstname or lastname or username or email or birthday_day or birthday_month or birthday_year):
        return {'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin.'}

    if username != currentUsername:
        try:
            User.objects.get(username=username)
            return {'success': False, 'message': 'Tên đăng nhập đã tồn tại.'}
        except User.DoesNotExist:
            pass
        except Exception as e:
            return {'success': False, 'message': 'Đã có lỗi xảy ra. Vui lòng thử lại sau.'}

    if email != currentEmail:
        try:
            User.objects.get(email=email)
            return {'success': False, 'message': 'Email đã tồn tại.'}
        except User.DoesNotExist:
            pass
        except Exception as e:
            return {'success': False, 'message': 'Đã có lỗi xảy ra. Vui lòng thử lại sau.'}

    if 6 < len(firstname) <= 20 and firstname.isalpha():
        return {'success': False, 'message': 'Họ phải có từ 2 - 20 ký tự, không chứa số, ký tự đặc biệt.'}

    if 6 < len(lastname) <= 20 and lastname.isalpha():
        return {'success': False, 'message': 'Tên phải có từ 2 - 20 ký tự, không chứa số, ký tự đặc biệt.'}

    if 6 < len(username) <= 20 and username.isalnum():
        return {'success': False, 'message': 'Tên đăng nhập phải có từ 2 - 20 ký tự, không chứa ký tự đặc biệt.'}

    birthday = date(int(birthday_year), int(birthday_month), int(birthday_day))
    if birthday != date(1920, 1, 1) and birthday > date.today() - timedelta(days=365 * 10):
        return {'success': False, 'message': 'Bạn chưa đủ tuổi để đăng ký tài khoản.'}
    if birthday != date(1920, 1, 1) and birthday.day < 1 or birthday.day > 31:
        return {'success': False, 'message': 'Ngày sinh không hợp lệ.'}

    if birthday != date(1920, 1, 1) and birthday.month < 1 or birthday.month > 12:
        return {'success': False, 'message': 'Tháng sinh không hợp lệ.'}

    return {'success': True, 'message': 'Validated.'}


def blogValidate(title, content, collections, image):
    if not title:
        return {'success': False, 'message': 'Vui lòng nhập tiêu đề.'}
    if not content:
        return {'success': False, 'message': 'Vui lòng nhập nội dung.'}
    if not collections:
        return {'success': False, 'message': 'Vui lòng chọn bộ sưu tập.'}
    if not image:
        return {'success': False, 'message': 'Vui lòng chọn ảnh bìa.'}

    if len(title) > 100:
        return {'success': False, 'message': 'Tiêu đề không được vượt quá 100 ký tự.'}

    if len(content) > 100000:
        return {'success': False, 'message': 'Nội dung không được vượt quá 100000 ký tự.'}

    return {'success': True, 'message': 'Mọi thứ đều hợp lệ.'}


def editBlogValidate(title, content, image, collectionsId):
    if not title:
        return {'success': False, 'message': 'Vui lòng nhập tiêu đề.'}
    if not content:
        return {'success': False, 'message': 'Vui lòng nhập nội dung.'}
    if not collectionsId:
        return {'success': False, 'message': 'Vui lòng chọn bộ sưu tập.'}

    if len(title) > 100:
        return {'success': False, 'message': 'Tiêu đề không được vượt quá 100 ký tự.'}

    if len(content) > 100000:
        return {'success': False, 'message': 'Nội dung không được vượt quá 100000 ký tự.'}

    return {'success': True, 'message': 'Mọi thứ đều hợp lệ.'}
