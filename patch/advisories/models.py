from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Advisory(models.Model):
    """
    "Lowest common denominator" across all vendor advisories.
    """

    upstream_id = models.CharField(max_length=200, verbose_name="Upstream ID", help_text="The ID used by the vendor to refer to this advisory")
    short_description = models.CharField(max_length=200, null=True, help_text="One-line description of the advisory")
    description = models.TextField(null=True, help_text="Longer description of the advisory")
    action = models.TextField(null=True, help_text="What, if any, actions need to be taken to address the advisory")
    issued = models.DateTimeField(default=timezone.now, help_text="Date and time at which the advisory was issued")
    source = models.CharField(choices=settings.ADVISORY_SOURCES, max_length=32, help_text="Vendor source of the advisory")
    severity = models.IntegerField(blank=True, choices=settings.ADVISORY_SEVERITIES, default=0, help_text="Local severity of the advisory, once it has been reviewed")
    reviewed_by = models.ForeignKey(User, blank=True, null=True, help_text="Person who locally reviewed the advisory for its overall severity (or None if the severity was determined automatically)")
    search_packages = models.TextField(blank=True, null=True, help_text="Space separated list of source and binary packages used to speed up search")

    class Meta:
        verbose_name_plural = "advisories"
        ordering = ["-issued"]

    def __unicode__(self):
        return self.upstream_id

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('advisory_detail', args=(self.upstream_id, ))

    def source_package_names(self):
        return ", ".join([package.__unicode__() for package in self.sourcepackage_set.all()])

    def source_url(self):
        return dict(settings.SOURCE_ADVISORY_DETAIL_URLS)[self.source] % self.upstream_id

    def formal_upstream_id(self):
        if self.source == 'ubuntu':
            return "USN-%s" % self.upstream_id
        else:
            return self.upstream_id

class SourcePackage(models.Model):
    """
    Source package to which an advisory refers. These are not of a direct concern to hosts, as source packages are not actually "installed".

    For Debian advisories, the source package is used to determine what binary packages (and their versions) are considered safe.
    """

    advisory = models.ForeignKey(Advisory, help_text="Advisory to which this package belongs")
    package = models.CharField(max_length=200, help_text="Name of source package")
    release = models.CharField(choices=settings.RELEASES,max_length=32, help_text="Specific release to which this package belongs")
    safe_version = models.CharField(max_length=200, help_text="Package version that is to be considered 'safe' at the issue of this advisory")

    class Meta:
        verbose_name_plural = "source packages"
        ordering = ["-package"]

    def __unicode__(self):
        safe_version = self.safe_version

        if self.safe_version == '0':
            safe_version = ''

        return "%s %s (%s)" % (self.package, safe_version, self.release)

    def source_url(self):
        return dict(settings.SOURCE_PACKAGE_DETAIL_URLS)[self.advisory.source] % (self.release, self.package)

class BinaryPackage(models.Model):
    """
    Binary package to which an advisory refers.

    In the case of Ubuntu, these are resolved directly from the supplied JSON data. For Debian these will be generated based on the source packages
    associated with this advisory.

    If source_package is null it is because this binary package was created directly from external data, rather than being generated locally.
    """

    advisory = models.ForeignKey(Advisory, help_text="Advisory to which this package belongs")
    source_package = models.ForeignKey(SourcePackage, blank=True, null=True, help_text="If set, the source package from which this binary package was generated")
    package = models.CharField(max_length=200, help_text="Name of binary package")
    release = models.CharField(choices=settings.RELEASES,max_length=32, help_text="Specific release to which this package belongs")
    safe_version = models.CharField(max_length=200, null=True, help_text="Package version that is to be considered 'safe' at the issue of this advisory")
    architecture = models.CharField(max_length=200, null=True, help_text="Machine architecture")

    class Meta:
        verbose_name_plural = "binary packages"
        ordering = ["-package"]

    def __unicode__(self):
        if self.safe_version:
            return "%s %s (%s, %s)" % (self.package, self.safe_version, self.release, self.architecture)
        else:
            return "%s (%s, %s)" % (self.package, self.release, self.architecture)

    def source_url(self):
        return dict(settings.SOURCE_PACKAGE_DETAIL_URLS)[self.advisory.source] % (self.release, self.package)
