# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogVideoList
from ImageTools import *
from BaseClasses import DialogBaseInfo


class DialogEpisodeInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.tmdb_id = kwargs.get('show_id')
        self.season = kwargs.get('season')
        self.showname = kwargs.get('tvshow')
        self.episodenumber = kwargs.get('episode')
        if self.tmdb_id or self.showname:
            self.data = extended_episode_info(self.tmdb_id, self.season, self.episodenumber)
            if not self.data:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                return
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            search_string = "%s tv" % (self.data["general"]["Title"])
            youtube_thread = Get_Youtube_Vids_Thread(search_string, "", "relevance", 15)
            youtube_thread.start()
            if "DBID" not in self.data["general"]:  # need to add comparing for episodes
                poster_thread = Threaded_Function(Get_File, self.data["general"]["Poster"])
                poster_thread.start()
            if "DBID" not in self.data["general"]:
                poster_thread.join()
                self.data["general"]['Poster'] = poster_thread.listitems
            filter_thread = Filter_Image_Thread(self.data["general"]["Poster"], 25)
            filter_thread.start()
            youtube_thread.join()
            self.youtube_vids = youtube_thread.listitems
            filter_thread.join()
            self.data["general"]['ImageFilter'], self.data["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
        else:
            Notify(ADDON.getLocalizedString(32143))
            self.close()
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        super(DialogEpisodeInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.data["general"]["ImageColor"])
        self.window.setProperty("type", "episode")
        passDictToSkin(self.data["general"], "movie.", False, False, self.windowid)
        self.getControl(1000).addItems(create_listitems(self.data["actors"], 0))
        self.getControl(750).addItems(create_listitems(self.data["crew"], 0))
        self.getControl(1150).addItems(create_listitems(self.data["videos"], 0))
        self.getControl(350).addItems(create_listitems(self.youtube_vids, 0))
        self.getControl(1350).addItems(create_listitems(self.data["images"], 0))

    def onClick(self, controlID):
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if controlID in [1000, 750]:
            actor_id = self.getControl(controlID).getSelectedItem().getProperty("id")
            credit_id = self.getControl(controlID).getSelectedItem().getProperty("credit_id")
            AddToWindowStack(self)
            self.close()
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id, credit_id=credit_id)
            dialog.doModal()
        elif controlID in [350, 1150]:
            listitem = self.getControl(controlID).getSelectedItem()
            AddToWindowStack(self)
            self.close()
            self.movieplayer.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, True)
            self.movieplayer.wait_for_video_end()
            PopWindowStack()
        elif controlID in [1250, 1350]:
            image = self.getControl(controlID).getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif controlID == 132:
            w = TextViewer_Dialog('DialogTextViewer.xml', ADDON_PATH, header=ADDON.getLocalizedString(32037), text=self.season["general"]["Plot"], color=self.season["general"]['ImageColor'])
            w.doModal()
        elif controlID == 6001:
            rating = get_rating_from_user()
            if rating:
                identifier = [self.tmdb_id, self.season, self.data["general"]["episode"]]
                send_rating_for_media_item("episode", identifier, rating)
                self.UpdateStates()
        elif controlID == 6006:
            self.ShowRatedEpisodes()

    def UpdateStates(self, forceupdate=True):
        if forceupdate:
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            self.update = extended_episode_info(self.tmdb_id, self.season, self.episodenumber, 0)
            self.data["account_states"] = self.update["account_states"]
        if self.data["account_states"]:
            # if self.data["account_states"]["favorite"]:
            #     self.window.setProperty("FavButton_Label", "UnStar episode")
            #     self.window.setProperty("movie.favorite", "True")
            # else:
            #     self.window.setProperty("FavButton_Label", "Star episode")
            #     self.window.setProperty("movie.favorite", "")
            if self.data["account_states"]["rated"]:
                self.window.setProperty("movie.rated", str(self.data["account_states"]["rated"]["value"]))
            else:
                self.window.setProperty("movie.rated", "")
            # self.window.setProperty("movie.watchlist", str(self.data["account_states"]["watchlist"]))
            # Notify(str(self.data["account_states"]["rated"]["value"]))

    def ShowRatedEpisodes(self):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        listitems = get_rated_media_items("tv/episodes")
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.OpenVideoList(listitems=listitems)
