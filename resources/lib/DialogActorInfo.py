import os
import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
from DialogVideoInfo import DialogVideoInfo
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))
homewindow = xbmcgui.Window(10000)

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")


class DialogActorInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.id = kwargs.get('id')
        name = kwargs.get('name')
        if not self.id and name:
            names = name.split(" / ")
            if len(names) > 1:
                Dialog = xbmcgui.Dialog()
                ret = Dialog.select("Actor Info", names)
                if ret == -1:
                    return False
                name = names[ret]
            clean_name = name.split(" as ")[0]
            self.id = GetPersonID(clean_name)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        if self.id:
            self.person, self.movie_roles, self.tvshow_roles, self.images = GetExtendedActorInfo(self.id)
            name = self.person["name"]
            self.youtube_vids = GetYoutubeSearchVideos(name)
            homewindow.setProperty("actor.Title", name)
            homewindow.setProperty("actor.TotalMovies", str(len(self.movie_roles)))
            homewindow.setProperty("actor.Biography", self.person["biography"])
            homewindow.setProperty("actor.Birthday", self.person["birthday"])
            homewindow.setProperty("actor.Thumb", self.person["thumb"])
            homewindow.setProperty("actor.id", self.person["id"])
            homewindow.setProperty("actor.AlsoKnownAs", self.person["also_known_as"])
            homewindow.setProperty("actor.Description", self.person["description"])
            homewindow.setProperty("actor.PlaceOfBirth", self.person["place_of_birth"])
            homewindow.setProperty("actor.DeathDay", self.person["deathday"])
            homewindow.setProperty("actor.Homepage", self.person["homepage"])
        else:
            Notify("No ID found")
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        movie_listitems = CreateListItems(self.movie_roles)
        tvshow_listitems = CreateListItems(self.tvshow_roles)
        image_listitems = CreateListItems(self.images)
        youtube_listitems = CreateListItems(self.youtube_vids)
        self.getControl(150).addItems(movie_listitems)
        # self.getControl(250).addItems(image_listitems)
        self.getControl(350).addItems(youtube_listitems)
        xbmc.executebuiltin("SetFocus(150)")
    #    self.getControl(150).addItems(tvshow_listitems)

    def setControls(self):
        pass

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == 150:
            listitem = self.getControl(150).getSelectedItem()
            dialog = DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % __addonname__, __cwd__, id=listitem.getProperty("id"), dbid=listitem.getProperty("dbid"))
            dialog.doModal()

    def onFocus(self, controlID):
        pass
