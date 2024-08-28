from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializer import UserSerializer
from django.core.files.storage import FileSystemStorage, default_storage
# Ensure this path is correct
from api.ml_model.Cr_Couting import counting
from datetime import datetime, timedelta


@api_view(["GET", "POST", "DELETE"])
def get_crowd(request):
    if request.method == "GET":
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
        # return Response({"status": "GET request processed"})

    elif request.method == "POST":
        # return Response({"status": "POST request processed"})
        if "image" not in request.FILES:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            image = request.FILES["image"]
            time = request.data["time"]
            fs = FileSystemStorage()
            filename = default_storage.save(image.name, image)
            uploaded_file_url = fs.path(filename)
            crowd_count = counting(uploaded_file_url)
            user = User(image=uploaded_file_url,
                        crowd_count=crowd_count, time=time)
            user.save()
            time = user.time

            user_time = datetime.fromisoformat(time.replace("Z", "+00:00"))

            # Retrieve the last 3 records within the last hour based on user time
            # user_time - timedelta(minutes=5)
            time_span = user_time - timedelta(minutes=5)
            recent_users = User.objects.filter(
                time__gte=time_span, time__lte=user_time).order_by('-time')[:3]

            # Analyze the crowd counts
            crowd_sizes = [u.crowd_count for u in recent_users]
            if len(crowd_sizes) >= 2:
                if all(size > 100 for size in crowd_sizes):
                    alert = "High crowd of {} people".format(crowd_sizes[0])
                elif crowd_sizes[0] > crowd_sizes[1]:
                    alert = "Crowd is gathering. Was at {} people, Now at {} people".format(crowd_sizes[1],
                                                                                            crowd_sizes[0])
                elif crowd_sizes[0] < crowd_sizes[1]:
                    alert = "Crowd is dispersing. Was at {} people, Now at {} people".format(crowd_sizes[1],
                                                                                             crowd_sizes[0])
                else:
                    alert = "Small crowd of {} people".format(crowd_sizes[0])
            else:
                if all(size > 100 for size in crowd_sizes):
                    alert = "High crowd of {} people".format(crowd_sizes[0])
                else:
                    alert = "Small crowd of {} people".format(crowd_sizes[0])

            user.alert = alert
            user.save()

            alert = user.alert
            return Response({"status": "Image uploaded", "Crowd_Size": crowd_count, "Time": time, "Alert": alert}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == "DELETE":
        try:
            User.objects.all().delete()
            return Response({"status": "All images deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
