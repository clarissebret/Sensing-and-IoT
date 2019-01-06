import sys
sys.path.append('/Users/Clarisse/google-cloud-sdk/platform/google_appengine')

from google.appengine.ext import vendor

#Add any libraries installed in the "lib" folder.
vendor.add('lib')