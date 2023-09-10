# from rest_framework.decorators import api_view
# from rest_framework.views import APIView
# from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework import status
from rest_framework import viewsets

from .models import Recipe
from .serializers import RecipeSerializer

# Вью функции

# @api_view(['GET', 'POST'])
# def api_recipes(request):
#     if request.method == 'POST':
#         serializer = RecipeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     recipes = Recipe.objects.all()
#     serializer = RecipeSerializer(recipes, many=True)
#     return Response(serializer.data)

# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def api_recipes_detail(request, pk):
#     recipe = Recipe.objects.get(pk=pk)
#     if request.method == 'PUT' or request.method == 'PATCH':
#         serializer = RecipeSerializer(recipe, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'DELETE':
#         recipe.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     serializer = RecipeSerializer(recipe)
#     return Response(serializer.data)

# Вью классы низкоуровневые

# class APIRecipe(APIView):
#     def get(self, request):
#         recipes = Recipe.objects.all()
#         serializer = RecipeSerializer(recipes, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = RecipeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED) 
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Высокоуровневые дженерики

# class RecipeList(generics.ListCreateAPIView):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer


# class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer 

# Высокоуровневые вьюсеты

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer 
