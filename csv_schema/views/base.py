class ViewableItems:
    """Only return viewable items in child views."""
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().viewable(self.request.user)
