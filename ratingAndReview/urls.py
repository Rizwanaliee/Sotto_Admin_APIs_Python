from django.urls import path
from ratingAndReview import views

urlpatterns = [
    path('get/provider/detail/fav',views.GetProviderDetailForFavourite.as_view()),
    path('add/favourite', views.MarkFavouriteProvider.as_view()),
    path('remove/favourite',views.RemoveFavouriteProvider.as_view()),
    path('favourite/providers', views.FavouriteProviderList.as_view()),
    path('rating/review', views.RatingAndReviewView.as_view()),
    path('top/rated/providers', views.TopRatedProviders.as_view()),
    path('rating/review/with/average', views.RatingAndReviewsWithAverageRate.as_view())
]
