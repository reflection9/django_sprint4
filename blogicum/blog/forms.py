from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Класс формы постов."""

    class Meta:
        model = Post
        exclude = ['author']

        widgets = {
            'pub_date': forms.DateInput(attrs={
                'type': 'date',
            }),
        }


class CommentForm(forms.ModelForm):
    """Класс комментариев к постам."""

    class Meta:
        model = Comment
        fields = ['text']

        widgets = {
            'text': forms.Textarea()
        }
