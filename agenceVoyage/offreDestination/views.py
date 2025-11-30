from .models import Offre, Destination
from django.shortcuts import render, get_object_or_404

from .models import Hebergement

def liste_hebergements(request):
    hebergements = Hebergement.objects.all()
    return render(request, "hebergements/liste_hebergements.html", {"hebergements": hebergements})


def hebergement_detail(request, pk):
    hebergement = get_object_or_404(Hebergement, pk=pk)
    return render(request, "hebergements/hebergement_detail.html", {"hebergement": hebergement})

def liste_offres(request):
    offres = Offre.objects.all()
    return render(request, "offres/liste_offres.html", {"offres": offres})
def offre_detail(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    return render(request, 'offres/offre_detail.html', {'offre': offre})


def liste_destinations(request):
    destinations = Destination.objects.all()
    return render(request, "offres/liste_destinations.html", {"destinations": destinations})
def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    return render(request, 'offres/details.html', {'destination': destination})


from .forms import FiltreOffresForm

def liste_offres(request):
    form = FiltreOffresForm(request.GET or None)
    offres = Offre.objects.filter(actif=True)

    if form.is_valid():
        destination = form.cleaned_data.get('destination')
        prix_min = form.cleaned_data.get('prix_min')
        prix_max = form.cleaned_data.get('prix_max')

        if destination:
            offres = offres.filter(nom_destinations=destination)
        if prix_min is not None:
            offres = offres.filter(prix_par_personne__gte=prix_min)
        if prix_max is not None:
            offres = offres.filter(prix_par_personne__lte=prix_max)

    context = {
        'form': form,
        'offres': offres
    }
    return render(request, 'offres/liste_offres.html', context)


def home(request):
    recent_ids = request.session.get("recent_offers", [])
    recent_offres = Offre.objects.filter(id__in=recent_ids)

    return render(request, "home.html", {
        "recent_offres": recent_offres
    })

def offre_detail(request, pk):
    offre = get_object_or_404(Offre, pk=pk)

    # ---- SAVING RECENT VIEWS ----
    recent = request.session.get("recent_offers", [])

    # Assurer que ce sont des int
    recent = list(map(int, recent))

    # retirer si déjà présent
    if pk in recent:
        recent.remove(pk)

    # mettre au début
    recent.insert(0, pk)

    # garder max 5
    recent = recent[:5]

    request.session["recent_offers"] = recent
    request.session.modified = True

    return render(request, 'offres/offre_detail.html', {'offre': offre})
