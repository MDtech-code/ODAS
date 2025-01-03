from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Article, Comment
from .forms import ArticleForm, CommentForm
from django.contrib.auth.decorators import login_required
from app.account.models import Patient
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views import View
from django.db.models import Q
from app.core.utils.pagination import paginate_queryset

# Article Views


class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
      # Default to 1 if no page parameter
    
    def get_queryset(self):
        query = self.request.GET.get('search', '')
        if query:
            # Use Q objects for case-insensitive search by doctor name and title
            return Article.objects.select_related("doctor").filter(
                Q(doctor__user__username__icontains=query) | 
                Q(title__icontains=query)
            ).order_by("-created_at")
        return Article.objects.select_related("doctor").order_by("-created_at")

# class ArticleListView(ListView):
#     model = Article
#     template_name = "blog/article_list.html"
#     context_object_name = "articles"

#     def get_queryset(self):
#         return Article.objects.select_related("doctor").order_by("-created_at")


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"

class ArticleCreateView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'doctor':
            return HttpResponseForbidden("You are not authorized to create an article.")
        form = ArticleForm()
        context = { 'form': form, 'form_title': 'Create Article', 'button_text': 'Create' }
        return render(request, 'blog/article_form.html', context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'doctor':
            return HttpResponseForbidden("You are not authorized to create an article.")
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.doctor = request.user.doctor  # Assuming the doctor is linked to the user
            article.save()
            return redirect(reverse('article_detail', kwargs={'pk': article.pk}))
        return render(request, 'blog/article_form.html', {'form': form})
# class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
#     model = Article
#     form_class = ArticleForm
#     template_name = "blog/article_create.html"
#     success_url = reverse_lazy("article_list")

#     def form_valid(self, form):
#         form.instance.doctor = self.request.user.doctor
#         return super().form_valid(form)

#     def test_func(self):
#         return self.request.user.is_authenticated and self.request.user.user_type == 'doctor'

class ArticleUpdateView(View):
    def get(self, request, pk, *args, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        if article.doctor.user != request.user:
            return HttpResponseForbidden("You are not authorized to edit this article.")
        form = ArticleForm(instance=article)
        context = { 'form': form, 'form_title': 'Update Article', 'button_text': 'Update' }
        return render(request, 'blog/article_form.html', context)

    def post(self, request, pk, *args, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        if article.doctor.user != request.user:
            return HttpResponseForbidden("You are not authorized to edit this article.")
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect(reverse('article_detail', kwargs={'pk': article.pk}))
        return render(request, 'blog/article_form.html', {'form': form})
# class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Article
#     form_class = ArticleForm
#     template_name = "blog/article_update.html"
#     success_url = reverse_lazy("article_list")

# def test_func(self):
#     article = self.get_object()
#     return self.request.user.is_authenticated and self.request.user == article.doctor.user

class ArticleDeleteView(View):
    def get(self, request, pk, *args, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        if article.doctor.user != request.user:
            return HttpResponseForbidden("You are not authorized to delete this article.")
        return render(request, 'blog/article_delete.html', {'article': article})

    def post(self, request, pk, *args, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        if article.doctor.user != request.user:
            return HttpResponseForbidden("You are not authorized to delete this article.")
        article.delete()
        return redirect(reverse('article_list'))
# class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Article
#     template_name = "blog/article_delete.html"
#     success_url = reverse_lazy("article_list")

#     def test_func(self):
#         article = self.get_object()
#         return self.request.user.is_authenticated and self.request.user == article.doctor.user

# Comment Views
# class CommentModerationView(LoginRequiredMixin, UserPassesTestMixin, ListView):
#     model = Comment
#     template_name = "blog/comment_moderation.html"
#     context_object_name = "comments"

#     def get_queryset(self):
#         return Comment.objects.filter(article__doctor=self.request.user.doctor, is_approved=False)

#     def test_func(self):
#         return self.request.user.is_authenticated and self.request.user.user_type == 'doctor'

class AddCommentView(View):
    def post(self, request, article_id, *args, **kwargs):
        article = get_object_or_404(Article, id=article_id)
        patient = get_object_or_404(Patient, user=request.user)  # Ensure the logged-in user is a patient
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.patient = patient
            comment.save()
            return redirect('article_detail', pk=article.id)
        return redirect('article_detail', pk=article.id) 
# @login_required
# def add_comment(request, article_id):
#     article = get_object_or_404(Article, id=article_id)
#     patient = Patient.objects.get(user=request.user) 
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.article = article
#             comment.patient = patient
#             comment.save()
#             return redirect('article_detail', pk=article.id)
#     else:
#         form = CommentForm()
#     return redirect('article_detail', pk=article.id)

class CommentModerationView(ListView):
    model = Comment
    template_name = 'blog/comment_moderation.html'
    context_object_name = 'comments'

    def get_queryset(self):
        return Comment.objects.filter(article__author=self.request.user)



class ApproveCommentView(View):
    def post(self, request, pk, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=pk)

        # Ensure that only the doctor who wrote the article can approve the comment
        if comment.article.doctor.user == request.user:
            comment.is_approved = True
            comment.save()
        else:
            return HttpResponseForbidden("You are not authorized to approve this comment.")
        
        return redirect('comment_moderation')
# @login_required
# def approve_comment(request, pk):
#     comment = get_object_or_404(Comment, pk=pk)
#     if comment.article.author == request.user:  # Ensure only the author of the article can approve
#         comment.approved = True
#         comment.save()
#     return redirect('comment_moderation')


class DeleteCommentView(View):
    def post(self, request, pk, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=pk)

        # Ensure that only the doctor who wrote the article or the patient who wrote the comment can delete it
        if comment.article.doctor.user == request.user or comment.patient.user == request.user:
            comment.delete()
        else:
            return HttpResponseForbidden("You are not authorized to delete this comment.")
        
        return redirect('comment_moderation')
# @login_required
# def delete_comment(request, pk):
#     comment = get_object_or_404(Comment, pk=pk)
#     if comment.article.author == request.user or comment.author == request.user:
#         comment.delete()
#     return redirect('comment_moderation')