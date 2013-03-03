__author__ = 'Artiom'


class UploadPage(BlogHandler):

    def get(self):
        #upload_url = blobstore.create_upload_url('/upload')
        if self.user:
            next_url=self.request.headers.get('referer','/')
            logging.error("next url1 %s" %next_url)
            self.render("pic_upload.html", upload_url='/upload', page_name = next_url)
        else:
            self.redirect('/login')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)