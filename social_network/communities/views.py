from django.contrib import messages
from django.contrib.auth.mixins import(LoginRequiredMixin,PermissionRequiredMixin)

from django.urls import reverse

from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render

from django.views import generic
from communities.models import Community, CommunityMember
from . import models
from braces.views import SelectRelatedMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateCommunity(LoginRequiredMixin,generic.CreateView):
    fields = ("name", "description")
    model = Community

class SingleCommunity(generic.DetailView):
    model = Community

class ListCommunity(generic.ListView):
    model = Community

class JoinCommunity(LoginRequiredMixin, generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse("communities:single", kwargs={"slug": self.kwargs.get("slug")})

    def get(self, request, *args, **kwargs):
        community = get_object_or_404(Community, slug=self.kwargs.get("slug"))

        try:
            CommunityMember.objects.create(user=self.request.user,community=community)
        except IntegrityError:
            messages.warning(self.request,("Warning, already a member of {}".format(community.name)))

        else:
            messages.success(self.request,"You are now a member of the {} community.".format(community.name))

        return super().get(request, *args, **kwargs)


class LeaveCommunity(LoginRequiredMixin, generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse("communities:single",kwargs={"slug": self.kwargs.get("slug")})

    def get(self, request, *args, **kwargs):
        try:
            membership = models.CommunityMember.objects.filter(
                user=self.request.user,
                community__slug=self.kwargs.get("slug")
            ).get()

        except models.CommunityMember.DoesNotExist:
            messages.warning(
                self.request,
                "You can't leave this community because you aren't in it."
            )

        else:
            membership.delete()
            messages.success(self.request,"You have successfully left this group.")
        return super().get(request, *args, **kwargs)

class DeleteCommunity(LoginRequiredMixin,SelectRelatedMixin,generic.DeleteView):
    model = Community
    select_related = ("user", "community")
    success_url = reverse_lazy("community:all")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Community Deleted")
        return super().delete(*args, **kwargs)
