from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from drawbud.models import *
import re
MAX_UPLOAD_SIZE = 2500000

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200,
                               widget=forms.PasswordInput())
    # check validation of the data
    def clean(self):

        # get the cleaned_data from the parent class
        cleaned_data = super().clean()
        
        # check the username/password pairs in the registered users
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        # check if the username and password is valid
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError({'username': ["Invalid username/password"]})

        return cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200,
                               label="Password",
                               widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=200,
                                       label="Confirm password",
                                       widget=forms.PasswordInput())
    email = forms.CharField(max_length=50, widget=forms.EmailInput())
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)

    def clean(self):
        
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError({'password': ["Passwords did not match."],
                                         'confirm_password': ["passwords did not match"]})

        return cleaned_data
    
    # get the cleaned data and process the specific field
    def clean_username(self):
        
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # must return the field we got from the cleaned data
        return username


# For pictures
class ItemForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('profile_picture',)
		# fields = ('profile_picture', 'bio_text',)


	def clean_picture(self):
		picture = self.cleaned_data['profile_picture']
		try:
			
			if not picture:
				raise forms.ValidationError('You must upload a picture')
			
			if not picture.content_type or not picture.content_type.startswith('image'):
				raise forms.ValidationError('File type is not image')
			if picture.size > MAX_UPLOAD_SIZE:
				raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))

		except AttributeError:
			pass
		return picture

# For Room
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('room_name', 'max_player_number', 'description')

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_room_name(self):
        
        roomname = self.cleaned_data.get("room_name")
        	
        if Room.objects.filter(room_name__exact=roomname):
            raise forms.ValidationError("Room name is already taken.")


        # must return the field we got from the cleaned data
        return roomname
