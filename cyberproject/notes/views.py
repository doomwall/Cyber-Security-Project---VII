from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Note


@login_required
def note_list(request):
    """Show the notes belonging to the logged-in user."""
    notes = Note.objects.filter(owner=request.user)
    return render(request, 'notes/list.html', {'notes': notes})


@login_required
def note_detail(request, note_id):
    """Show one note.

    ###################################################################
    # FLAW 1 -- OWASP A01:2021 Broken Access Control
    #           Insecure Direct Object Reference (IDOR), CWE-639
    #
    # The view checks AUTHENTICATION (@login_required: "are you logged
    # in?") but never AUTHORISATION ("is this note yours?"). Any logged-in
    # user can read any note by changing the number in the URL, because
    # the note id is a guessable, sequential integer.
    #
    # To repair the app: comment out the VULNERABLE line and uncomment
    # the SECURE line.
    ###################################################################
    """

    # --- SECURE version: scope the lookup to the owner, so somebody
    # --- else's note does not exist as far as this view is concerned.
    # note = get_object_or_404(Note, pk=note_id, owner=request.user)

    # --- VULNERABLE version: fetch by id alone and trust the URL.
    note = get_object_or_404(Note, pk=note_id)

    return render(request, 'notes/detail.html', {'note': note})


@login_required
def note_create(request):
    error = None

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        if title:
            note = Note.objects.create(
                owner=request.user,
                title=title,
                body=body,
            )
            return redirect('note_detail', note_id=note.pk)
        error = 'Title is required.'

    return render(request, 'notes/form.html', {'error': error})


@login_required
@require_POST
def note_delete(request, note_id):
    """Delete one note. Requires POST (so it cannot be triggered by a link
    or an image tag) and is scoped to the owner."""
    note = get_object_or_404(Note, pk=note_id, owner=request.user)
    note.delete()
    return redirect('note_list')
