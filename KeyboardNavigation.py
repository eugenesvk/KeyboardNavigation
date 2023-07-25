import sublime, sublime_plugin
import string

defDelims = [chr(32), chr(9), chr(10), chr(13), chr(34), chr(35), chr(36), chr(37), chr(38), chr(39), chr(61), chr(64), chr(58), chr(63), chr(46), chr(44), chr(43), chr(95), chr(45), chr(60), chr(62), chr(40), chr(41), chr(91), chr(93), chr(123), chr(125), chr(124), chr(47), chr(92)] # 32=space 9=tab 10=newline 13=carriagereturn 34=" 35=# 36=$ 37=% 38=& 39=' 61== 64=@ 58=: 63=? 46=. 44=, 43=+ 95=_ 45=- 60=< 62=> 40=( 41=) 91=[ 93=] 123={ 125=} 124=| 47=/ 92=\

#——————————  Dynamic caller command ——————————
class MoveKn(sublime_plugin.TextCommand):
  def run(self, edit, arg, subwordDelims=defDelims):
    moveT, direction, side, wordT, delimT = None, None, None, None, None
    if "▋" in arg:
      moveT	= "Select"
    else:
      moveT	= "Move"
    if "⎌" in arg:
      direction	= "Previous"
    if "↷" in arg:
      direction	= "Next"
    if "¦" in arg:
      delimT = "Boundary"
    if "¦w" in arg:
      side 	= "Beg"
      wordT	= "Subword"
    if "w¦" in arg:
      side 	= "End"
      wordT	= "Subword"
    if "¦W" in arg:
      side 	= "Beg"
      wordT	= "Bigword"
    if "W¦" in arg:
      side 	= "End"
      wordT	= "Bigword"
    if any(a is None for a in (direction, side, wordT)):
      return
    forward = True if (direction == "Next") else False
    clsName = f"{moveT}To{side}Of{wordT}{delimT}Command"
    clsMoveKn = globals()[clsName]
    clsMoveKn.run(self, edit, forward=forward, subwordDelims=subwordDelims)

#---------------------------------------------------------------
class MoveToBegOfContigBoundaryCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward):
    view = self.view
    # 32=space 9=tab 10=newline 13=carriagereturn
    whiteChars = (chr(32), chr(9), chr(10), chr(13))
    #spaceChars = (chr(32), chr(9))
    spaceChars = (chr(32), chr(9))
    newlineChars = (chr(10), chr(13))
    newlineChar = chr(10)
    # newlineChars = (chr(10), chr(13))
    RegionsSelOld = list(view.sel())
    view.sel().clear()
    for ThisRegion in RegionsSelOld:
    # for ThisRegion in view.sel():
      if(forward): #forward
        boolAtNewline = False
        ThisRegionBeg = ThisRegion.a
        ThisRegionEnd = ThisRegion.b
        if( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd < view.size()) ):
          ThisRegionEnd += 1
        else:
          while( ((view.substr(ThisRegionEnd) not in spaceChars) or (view.substr(ThisRegionEnd) in newlineChars)) and (ThisRegionEnd < view.size()) ):
            if(view.substr(ThisRegionEnd) == newlineChar):
              boolAtNewline = True
              ThisRegionEnd += 1
              break
            ThisRegionEnd += 1
          while( ((view.substr(ThisRegionEnd) in spaceChars) or boolAtNewline) and (ThisRegionEnd < view.size()) ):
            if(boolAtNewline):
              break
            ThisRegionEnd += 1
          if( (ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b) ):
            ThisRegionEnd += 1
        # view.sel().clear()
        view.sel().add(sublime.Region(ThisRegionEnd))
        view.show(ThisRegionEnd+1)
      else: #backward
        ThisRegionBeg = ThisRegion.a
        ThisRegionEnd = ThisRegion.b-1
        if( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd >= 0) ):
          ThisRegionEnd -= 1
        while( (view.substr(ThisRegionEnd) in spaceChars) and (ThisRegionEnd >= 0) ):
          ThisRegionEnd -= 1
        while( (view.substr(ThisRegionEnd) not in whiteChars) and (ThisRegionEnd >= 0) ):
          ThisRegionEnd -= 1
        if( (ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b) ):
          ThisRegionEnd -= 1
        # view.sel().clear()
        view.sel().add(sublime.Region(ThisRegionEnd+1))
        view.show(ThisRegionEnd)

# https://ee.hawaii.edu/~tep/EE160/Book/chap4/subsection2.1.1.1.html
class MoveToBegOfSubwordBoundaryCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward, subwordDelims=defDelims):
    view = self.view
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.a
      ThisRegionEnd = ThisRegion.b
      endAdd = 0; endShow = 1
      if(forward): # forward
        while((ThisRegionEnd < view.size()) and (view.substr(ThisRegionEnd) not in subwordDelims) ):
          ThisRegionEnd += 1
        if   ((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b) ):
          ThisRegionEnd += 1
      else:        # backward
        ThisRegionEnd -= 1
        while((ThisRegionEnd >= 0         ) and (view.substr(ThisRegionEnd) not in subwordDelims)):
          ThisRegionEnd -= 1
        if   ((ThisRegionEnd >= 0         ) and (ThisRegionEnd+1 == ThisRegion.b) ):
          ThisRegionEnd -= 1
        endAdd = 1; endShow = 0
      regionsNew += [sublime.Region(ThisRegionEnd+endAdd)]
    if regionsNew:
      view.sel().clear()
      view.sel().add_all(regionsNew)
      view.show(ThisRegionEnd+endShow)

class MoveToEndOfSubwordBoundaryCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward, subwordDelims=defDelims):
    view = self.view
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.a
      ThisRegionEnd = ThisRegion.b
      endAdd = 0; endShow = 1
      if(forward): # forward
        while((ThisRegionEnd < view.size()) and (view.substr(ThisRegionEnd)     in subwordDelims) ):
          ThisRegionEnd += 1 # skip beg delimiters '¦-ddd¦'
        while((ThisRegionEnd < view.size()) and (view.substr(ThisRegionEnd) not in subwordDelims) ):
          ThisRegionEnd += 1
        if   ((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b) ):
          ThisRegionEnd += 1
      else:        # backward
        ThisRegionEnd -= 1
        while((ThisRegionEnd >= 0         ) and (view.substr(ThisRegionEnd)     in subwordDelims)):
          ThisRegionEnd -= 1 # skip end delimiters '¦ddd-¦'
        while((ThisRegionEnd >= 0         ) and (view.substr(ThisRegionEnd) not in subwordDelims)):
          ThisRegionEnd -= 1
        if   ((ThisRegionEnd >= 0         ) and (ThisRegionEnd+1 == ThisRegion.b) ):
          ThisRegionEnd -= 1
        endAdd = 1; endShow = 0
      regionsNew += [sublime.Region(ThisRegionEnd+endAdd)]
    if regionsNew:
      view.sel().clear()
      view.sel().add_all(regionsNew)
      view.show(ThisRegionEnd+endShow)

#---------------------------------------------------------------
class SelectToBegOfContigBoundaryCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward):
    view = self.view
    # 32=space 9=tab 10=newline 13=carriagereturn
    whiteChars = (chr(32), chr(9), chr(10), chr(13))
    spaceChars = (chr(32), chr(9))
    newlineChars = (chr(10), chr(13))
    newlineChar = chr(10)
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.a
      ThisRegionEnd = ThisRegion.b
      endAdd = 0; endShow = 1
      if    (ThisRegionBeg == ThisRegionEnd):
        if(forward): #forward
          boolAtNewline = False
          if( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd < view.size()) ):
            ThisRegionEnd += 1
          else:
            while( ((view.substr(ThisRegionEnd) not in spaceChars) or (view.substr(ThisRegionEnd) in newlineChars)) and (ThisRegionEnd < view.size()) ):
              if(view.substr(ThisRegionEnd) == newlineChar):
                boolAtNewline = True
                ThisRegionEnd += 1
                break
              ThisRegionEnd += 1
            while( ((view.substr(ThisRegionEnd) in spaceChars) or boolAtNewline) and (ThisRegionEnd < view.size()) ):
              if(boolAtNewline):
                break
              ThisRegionEnd += 1
            if( (ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b) ):
              ThisRegionEnd += 1
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
        else: #backward
          ThisRegionEnd -= 1
          if( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) in spaceChars) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) not in whiteChars) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          if( (ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b) ):
            ThisRegionEnd -= 1
          endAdd = 1; endShow = 0
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
      elif  (ThisRegionBeg <  ThisRegionEnd):
        if(forward): #forward
          boolAtNewline = False
          if( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd < view.size()) ):
            ThisRegionEnd += 1
          else:
            while( ((view.substr(ThisRegionEnd) not in spaceChars) or (view.substr(ThisRegionEnd) in newlineChars)) and (ThisRegionEnd < view.size()) ):
              if(view.substr(ThisRegionEnd) == newlineChar):
                boolAtNewline = True
                ThisRegionEnd += 1
                break
              ThisRegionEnd += 1
            while( ((view.substr(ThisRegionEnd) in spaceChars) or boolAtNewline) and (ThisRegionEnd < view.size()) ):
              if(boolAtNewline):
                break
              ThisRegionEnd += 1
            if( (ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b) ):
              ThisRegionEnd += 1
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
        else: #backward
          ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd > ThisRegionBeg-1) and (ThisRegionEnd >= 0)):
            ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) in spaceChars) and (ThisRegionEnd > ThisRegionBeg-1) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) not in whiteChars) and (ThisRegionEnd > ThisRegionBeg-1) and (ThisRegionEnd >= 0)):
            ThisRegionEnd -= 1
          if((ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b)):
            ThisRegionEnd -= 1
          endAdd = 1; endShow = 0
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
      else: #ThisRegionBeg >  ThisRegionEnd
        if(forward): #forward
          boolAtNewline = False
          if( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd < view.size()) ):
            ThisRegionEnd += 1
          else:
            while( ((view.substr(ThisRegionEnd) not in spaceChars) or (view.substr(ThisRegionEnd) in newlineChars)) and (ThisRegionEnd < ThisRegionBeg) and (ThisRegionEnd < view.size())):
              if(view.substr(ThisRegionEnd) == newlineChar):
                boolAtNewline = True
                ThisRegionEnd += 1
                break
              ThisRegionEnd += 1
            while( ((view.substr(ThisRegionEnd) in spaceChars) or boolAtNewline) and (ThisRegionEnd < ThisRegionBeg) and (ThisRegionEnd < view.size())):
              if(boolAtNewline):
                break
              ThisRegionEnd += 1
            if((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b)):
              ThisRegionEnd += 1
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
        else: #backward
          ThisRegionEnd -= 1
          if( (view.substr(ThisRegionEnd) in newlineChars) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) in spaceChars) and (ThisRegionEnd >= 0)):
            ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) not in whiteChars) and (ThisRegionEnd >= 0)):
            ThisRegionEnd -= 1
          if((ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b)):
            ThisRegionEnd -= 1
          endAdd = 1; endShow = 0
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
    if regionsNew:
      view.sel().clear()
      view.sel().add_all(regionsNew)
      view.show(ThisRegionEnd+endShow)

class SelectToBegOfSubwordBoundaryCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward, subwordDelims=defDelims):
    view = self.view
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.a
      ThisRegionEnd = ThisRegion.b
      endAdd = 0; endShow = 1
      if(ThisRegion.a == ThisRegion.b):
        if(forward): #forward
          while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd < view.size()) ):
            ThisRegionEnd += 1
          if((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegionBeg)):
            ThisRegionEnd += 1
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
        else: #backward
          ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          if((ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegionBeg)):
            ThisRegionEnd -= 1
          endAdd = 1; endShow = 0
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
      elif(ThisRegion.a < ThisRegion.b):
        if(forward): #forward
          while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd < view.size()) ):
            ThisRegionEnd += 1
          if((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b)):
            ThisRegionEnd += 1
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
        else: #backward
          ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          if((ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b)):
            ThisRegionEnd -= 1
          endAdd = 1; endShow = 0
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
      else: # ThisRegion.a > ThisRegion.b
        if(forward): #forward
          while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd < view.size()) ):
            ThisRegionEnd += 1
          if((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b)):
            ThisRegionEnd += 1
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
        else: #backward
          ThisRegionEnd -= 1
          while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd >= 0) ):
            ThisRegionEnd -= 1
          if((ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b)):
            ThisRegionEnd -= 1
          endAdd = 1; endShow = 0
          regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
    if regionsNew:
      view.sel().clear()
      view.sel().add_all(regionsNew)
      view.show(ThisRegionEnd+endShow)

class SelectToKnLinelimitCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward):
    view = self.view
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.a
      ThisRegionEnd = ThisRegion.b
      endAdd = 0; endShow = 0
      if(forward): #forward
        ThisRegionEnd = view.line(ThisRegion).end()
        regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
      else: #backward
        ThisRegionEnd = view.line(ThisRegion).begin()
        regionsNew += [sublime.Region(ThisRegionBeg, ThisRegionEnd+endAdd)]
    if regionsNew:
      view.sel().clear()
      view.sel().add_all(regionsNew)
      view.show(ThisRegionEnd+endShow)

#---------------------------------------------------------------
class ExpandSelectionToDelimsCommand(sublime_plugin.TextCommand):
  def run(self, edit, subwordDelims=defDelims):
    view = self.view
    # 32=space 9=tab 10=newline 13=carriagereturn 34=" 35=# 36=$ 37=% 38=& 39=' 61== 64=@ 58=: 63=? 46=. 44=, 43=+ 95=_ 45=- 60=< 62=> 40=( 41=) 91=[ 93=] 123={ 125=} 124=| 47=/ 92=\
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.begin() - 1
      ThisRegionEnd = ThisRegion.end()
      if( (ThisRegion.begin() != ThisRegionEnd) and (view.substr(ThisRegionBeg) in subwordDelims) ):
        ThisRegionBeg -= 1
      while( (view.substr(ThisRegionBeg) not in subwordDelims) and (ThisRegionBeg >= 0) ):
        ThisRegionBeg -= 1
      ThisRegionBeg += 1

      if( (ThisRegion.begin() != ThisRegionEnd) and (view.substr(ThisRegionEnd) in subwordDelims) ):
        ThisRegionEnd += 1
      while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd < view.size()) ):
        ThisRegionEnd += 1

      # view.sel().clear()
      view.sel().add(sublime.Region(ThisRegionBeg, ThisRegionEnd))

class ExpandSelectionToQuotesCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    # 34=" 39='
    beginDelims = [chr(34), chr(39)]
    endDelims = [chr(34), chr(39)]
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.begin() - 1
      ThisRegionEnd = ThisRegion.end()
      while( (view.substr(ThisRegionBeg) not in beginDelims) and (ThisRegionBeg >= 0)):
        ThisRegionBeg -= 1
      ThisRegionBeg += 1

      while( (view.substr(ThisRegionEnd) not in endDelims) and (ThisRegionEnd < view.size())):
        ThisRegionEnd += 1

      # view.sel().clear()
      view.sel().add(sublime.Region(ThisRegionBeg, ThisRegionEnd))

class ExpandSelectionToBracketsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    # 60=< 62=> 40=( 41=) 91=[ 93=] 123={ 125=}
    # beginDelims = [chr(60), chr(40), chr(91), chr(123)]
    # endDelims = [chr(62), chr(41), chr(93), chr(125)]
    BracketDelims = [chr(60), chr(40), chr(91), chr(123), chr(62), chr(41), chr(93), chr(125)]
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.begin() - 1
      ThisRegionEnd = ThisRegion.end()
      # while( (view.substr(ThisRegionBeg) not in beginDelims) and (ThisRegionBeg >= 0)):
      while( (view.substr(ThisRegionBeg) not in BracketDelims) and (ThisRegionBeg >= 0)):
        ThisRegionBeg -= 1
      ThisRegionBeg += 1

      # while( (view.substr(ThisRegionEnd) not in endDelims) and (ThisRegionEnd < view.size())):
      while( (view.substr(ThisRegionEnd) not in BracketDelims) and (ThisRegionEnd < view.size())):
        ThisRegionEnd += 1

      # view.sel().clear()
      view.sel().add(sublime.Region(ThisRegionBeg, ThisRegionEnd))

class ExpandSelectionToWhitespaceCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    # 32=space 9=tab 10=newline 13=carriagereturn
    whiteChars = (chr(32), chr(9), chr(10), chr(13))
    for ThisRegion in view.sel():
      ThisRegionBeg = ThisRegion.begin() - 1
      while( (view.substr(ThisRegionBeg) not in whiteChars) and (ThisRegionBeg >= 0)):
        ThisRegionBeg -= 1
      ThisRegionBeg += 1

      ThisRegionEnd = ThisRegion.end()
      while( (view.substr(ThisRegionEnd) not in whiteChars) and (ThisRegionEnd < view.size())):
        ThisRegionEnd += 1

      # if(ThisRegionBeg != ThisRegionEnd):
      # view.sel().clear()
      view.sel().add(sublime.Region(ThisRegionBeg, ThisRegionEnd))
      # else:
      #   view.sel().add(sublime.Region(ThisRegionBeg, ThisRegionBeg))

#---------------------------------------------------------------
class KnLinelimitCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward):
    view = self.view
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionBeg = view.line(ThisRegion).begin()
      ThisRegionEnd = view.line(ThisRegion).end()
      if(forward): #forward
        regionTo    = ThisRegionEnd
        regionsNew += [regionTo]
      else: #backward
        regionTo    = ThisRegionBeg
        regionsNew += [regionTo]
    if regionsNew:
      view.sel().clear()
      view.sel().add_all(regionsNew)
      view.show(regionTo)

#---------------------------------------------------------------
class KnIndentCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward):
    view = self.view
    RegionsSelOld = list(view.sel())
    #view.sel().clear()
    for ThisRegion in RegionsSelOld:
      ThisRegionFullline = KnFullLine(view, ThisRegion)
      StrContent = view.substr(ThisRegionFullline)
      ListLinesStrContent = StrContent.splitlines(True)
      NumLines = len(ListLinesStrContent)
      ListLinesStrContentNew = list()
      if((NumLines == 0) and forward):
        view.replace(edit, ThisRegionFullline, chr(9))
        view.sel().clear()
        view.sel().add(sublime.Region(ThisRegion.begin()+1))
        view.show(ThisRegion.begin()+1)
      elif(forward): #forward
        for StrThisLine in ListLinesStrContent:
          ListLinesStrContentNew.append(chr(9)+StrThisLine)
        view.replace(edit, ThisRegionFullline, ''.join(ListLinesStrContentNew))
        view.sel().clear()
        view.sel().add(sublime.Region(ThisRegion.begin()+1, ThisRegion.end()+NumLines))
        view.show(ThisRegion.begin()+1)
      else: #backward
        NumLinesReplaced = 0
        for StrThisLine in ListLinesStrContent:
          if(StrThisLine[0] == chr(9)):
            NumLinesReplaced += 1
            ListLinesStrContentNew.append(StrThisLine[1:])
          else:
            ListLinesStrContentNew.append(StrThisLine)
        if(NumLinesReplaced == 0):
          #print("case lines none contain tabs at beginning")
          pass
        elif( (ThisRegion.begin() == ThisRegionFullline.begin()) and (ListLinesStrContent[0][0] == chr(9)) ):
          #print("case line 1 cursor at begining of line and contains tab")
          view.replace(edit, ThisRegionFullline, ''.join(ListLinesStrContentNew))
          view.show(ThisRegion.begin())
          view.sel().clear()
          view.sel().add(sublime.Region(ThisRegion.begin(), ThisRegion.end()-NumLinesReplaced+1))
        elif(ThisRegion.begin() == ThisRegionFullline.begin()):
          #print("case line 1 cursor at begininng of line - dont move selection back in beginning")
          view.replace(edit, ThisRegionFullline, ''.join(ListLinesStrContentNew))
          view.show(ThisRegion.begin())
          view.sel().clear()
          view.sel().add(sublime.Region(ThisRegion.begin(), ThisRegion.end()-NumLinesReplaced))
        elif(view.substr(ThisRegionFullline.begin()) != chr(9)):
          #print("case line 1 contains no tab at beginning - dont move selection back in beginning")
          view.replace(edit, ThisRegionFullline, ''.join(ListLinesStrContentNew))
          view.show(ThisRegion.begin())
          view.sel().clear()
          view.sel().add(sublime.Region(ThisRegion.begin(), ThisRegion.end()-NumLinesReplaced))
        else:
          #print("case general case - line 1 move selection back 1 - line last move selection back num of tabs removed")
          view.replace(edit, ThisRegionFullline, ''.join(ListLinesStrContentNew))
          view.show(ThisRegion.begin()-1)
          view.sel().clear()
          view.sel().add(sublime.Region(ThisRegion.begin()-1, ThisRegion.end()-NumLinesReplaced))

#---------------------------------------------------------------
class CopyFulllinesCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    clipboard = ''
    for ThisRegion in view.sel():
      strThisRegionFullline = view.substr(KnFullLine(view, ThisRegion))

      if( (strThisRegionFullline[-1] == chr(10)) or (strThisRegionFullline[-1] == chr(13)) ):
        clipboard += (strThisRegionFullline)
      else: # there was no newline found at the end - this means it is the last line in the document, so add a newline for it
        clipboard += (strThisRegionFullline + chr(10))
    sublime.set_clipboard(clipboard)

class CutFulllinesCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    clipboard = ''
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionFullline = KnFullLine(view, ThisRegion)
      clipboard += (view.substr(ThisRegionFullline))
      regionsNew += [ThisRegionFullline]
      # self.view.erase(edit, ThisRegionFullline)
    sublime.set_clipboard(clipboard)
    for reg in regionsNew:
      self.view.erase(edit, reg)
    view.sel().clear()
    view.sel().add(regionsNew[0].a)

#---------------------------------------------------------------
class KnPasteCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    for ThisRegion in view.sel():
      # view.run_command('paste');
      sublimeclipboard = sublime.get_clipboard()
      if(ThisRegion.a != ThisRegion.b):
        view.replace(edit, ThisRegion, sublimeclipboard)
      else:
        view.insert(edit, ThisRegion.a, sublimeclipboard)
        view.show(ThisRegion.a + len(sublimeclipboard) + 1)

#---------------------------------------------------------------
class PasteAboveLinesCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    for ThisRegion in view.sel():

      PosSelectionBeg = ThisRegion.begin()-1
      while( not( (view.substr(PosSelectionBeg) == chr(10)) or (view.substr(PosSelectionBeg) == chr(13)) ) and (PosSelectionBeg > 0) ):
        PosSelectionBeg -= 1
      PosSelectionBeg += 1

      sublimeclipboard = sublime.get_clipboard()
      if(sublimeclipboard[-1:] != chr(10)):
        #print("ended in a newline not, adding one")
        view.insert(edit, PosSelectionBeg, chr(10))
        view.insert(edit, PosSelectionBeg, sublimeclipboard)
      else:
        view.insert(edit, PosSelectionBeg, sublimeclipboard)

#---------------------------------------------------------------
# duplicates line above (instead of below like innate one)
class KnDuplicateLineCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    for ThisRegion in view.sel():

      PosSelectionBeg = ThisRegion.begin()
      PosSelectionEnd = ThisRegion.end()

      PosSelectionBeg -= 1
      while( (PosSelectionBeg >= 0) and not( (view.substr(PosSelectionBeg) == chr(10)) or (view.substr(PosSelectionBeg) == chr(13)) ) ):
        PosSelectionBeg -= 1
      PosSelectionBeg += 1

      if(PosSelectionBeg != PosSelectionEnd):
        PosSelectionEnd -= 1
      while( (PosSelectionEnd < view.size()) and not( (view.substr(PosSelectionEnd) == chr(10)) or (view.substr(PosSelectionEnd) == chr(13)) ) ):
        PosSelectionEnd += 1
      if(PosSelectionEnd != view.size()):
        PosSelectionEnd += 1 # add the newline that you found

      strThisRegionFullline = view.substr(sublime.Region(PosSelectionBeg, PosSelectionEnd))

      if(strThisRegionFullline[-1:] != chr(10)):
        view.insert(edit, PosSelectionBeg, chr(10))
        view.insert(edit, PosSelectionBeg, strThisRegionFullline)
      else:
        view.insert(edit, PosSelectionBeg, strThisRegionFullline)

#---------------------------------------------------------------
class BlanklineAddCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward):
    view = self.view
    RegionsSelOld = list(view.sel())
    # view.sel().clear()
    for thisregion in RegionsSelOld:
      if(forward): #forward
        posToInsertLineAt = KnFullLine(view, thisregion).end()
        #print(posToInsertLineAt)
        view.insert(edit, posToInsertLineAt, chr(10))
        # view.sel().add(sublime.Region(posToInsertLineAt))
      else: #backward
        posToInsertLineAt = KnFullLine(view, thisregion).begin()-1
        view.insert(edit, posToInsertLineAt+1, chr(10))
        # view.sel().add(sublime.Region(posToInsertLineAt+1))

#---------------------------------------------------------------
class DeleteToBegOfContigBoundaryCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward):
    view = self.view
    whiteChars = (chr(32), chr(9), chr(10), chr(13))
    spaceChars = (chr(32), chr(9))
    # newlineChars = (chr(10), chr(13))
    for ThisRegion in view.sel():
      if(ThisRegion.a != ThisRegion.b):
        view.erase(edit, sublime.Region(ThisRegion.begin(), ThisRegion.end()))
        # view.show(ThisRegionEnd) #dont show move
      elif(forward): #forward
        ThisRegionBeg = ThisRegion.a
        ThisRegionEnd = ThisRegion.b
        while( (view.substr(ThisRegionEnd) not in whiteChars) and (ThisRegionEnd < view.size())):
          ThisRegionEnd += 1
        while( (view.substr(ThisRegionEnd) in spaceChars) and (ThisRegionEnd < view.size())):
          ThisRegionEnd += 1
        if((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b)):
          ThisRegionEnd += 1
        view.erase(edit, sublime.Region(ThisRegionBeg, ThisRegionEnd))
        # view.show(ThisRegionEnd) #dont show move
      else: #backward
        ThisRegionBeg = ThisRegion.a
        ThisRegionEnd = ThisRegion.b-1
        while( (view.substr(ThisRegionEnd) in spaceChars) and (ThisRegionEnd >= 0)):
          ThisRegionEnd -= 1
        while( (view.substr(ThisRegionEnd) not in whiteChars) and (ThisRegionEnd >= 0)):
          ThisRegionEnd -= 1
        if((ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b)):
          ThisRegionEnd -= 1
        view.erase(edit, sublime.Region(ThisRegionBeg, ThisRegionEnd+1))
        view.show(ThisRegionEnd)

class DeleteToBegOfSubwordBoundaryCommand(sublime_plugin.TextCommand):
  def run(self, edit, forward, subwordDelims=defDelims):
    view = self.view
    for ThisRegion in view.sel():
      if(ThisRegion.a != ThisRegion.b):
        view.erase(edit, sublime.Region(ThisRegion.a, ThisRegion.b))
        # view.show(ThisRegionEnd) #dont show move
      elif(forward): #forward
        # ThisRegionBeg = ThisRegion.a
        ThisRegionEnd = ThisRegion.b
        while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd < view.size()) ):
          ThisRegionEnd += 1
        if((ThisRegionEnd < view.size()) and (ThisRegionEnd == ThisRegion.b)):
          ThisRegionEnd += 1
        view.erase(edit, sublime.Region(ThisRegion.a, ThisRegionEnd))
        # view.show(ThisRegionEnd) #dont show move
      else: #backward
        # ThisRegionBeg = ThisRegion.a
        ThisRegionEnd = ThisRegion.b-1
        while( (view.substr(ThisRegionEnd) not in subwordDelims) and (ThisRegionEnd >= 0) ):
          ThisRegionEnd -= 1
        if((ThisRegionEnd >= 0) and (ThisRegionEnd+1 == ThisRegion.b)):
          ThisRegionEnd -= 1
        view.erase(edit, sublime.Region(ThisRegion.a, ThisRegionEnd+1))
        view.show(ThisRegionEnd)

#---------------------------------------------------------------
class DeleteLineCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    for ThisRegion in view.sel():
      self.view.erase(edit, KnFullLine(view, ThisRegion))

class DeleteLineWoLinebreakCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    for ThisRegion in view.sel():
      self.view.erase(edit, view.line(ThisRegion))

class SelectLineCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    for ThisRegion in view.sel():
      view.sel().add(KnFullLine(view, ThisRegion))

class SelectLineWoLinebreakCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view
    regionsNew = []
    for ThisRegion in view.sel():
      ThisRegionBeg = view.line(ThisRegion).begin()
      ThisRegionEnd = view.line(ThisRegion).end()
      atchar = 0
      charsinline = ThisRegionEnd - ThisRegionBeg
      StrThisLine = view.substr(view.line(ThisRegion))
      while( (StrThisLine[atchar] == chr(9)) and (atchar < charsinline) ):
        atchar += 1
      beginpos = ThisRegionBeg + atchar
      regionsNew += [sublime.Region(beginpos, view.line(ThisRegion).end())]
    if regionsNew:
      view.sel().clear()
      view.sel().add_all(regionsNew)
      view.show(ThisRegionEnd)

#---------------------------------------------------------------
#https://forum.sublimetext.com/t/bug-full-line-api-returns-another-next-line-with-it-also-if-region-given-to-it-ends-in-a-new-newline-also/44140/7
#Reimplementation of full_line due to full_line bug in ST3 some versions.
def KnFullLine(mview, mRegion):
  view = mview

  PosSelectionBeg = mRegion.begin()
  PosSelectionEnd = mRegion.end()

  PosSelectionBeg -= 1
  while(not(any(view.substr(PosSelectionBeg) == ch for ch in [chr(10),chr(13)])) and (PosSelectionBeg >=0            ) ):
    PosSelectionBeg -= 1
  PosSelectionBeg += 1

  if(PosSelectionBeg != PosSelectionEnd):
    PosSelectionEnd -= 1
  while(not(any(view.substr(PosSelectionEnd) == ch for ch in [chr(10),chr(13)])) and (PosSelectionEnd <= view.size()-1) ):
    PosSelectionEnd += 1
  if(PosSelectionEnd != view.size()):
    PosSelectionEnd += 1 # add the newline that you found

  #print("PosSelectionBeg=" + str(PosSelectionBeg))
  #print("PosSelectionEnd=" + str(PosSelectionEnd))
  ThisRegionFullline = sublime.Region(PosSelectionBeg, PosSelectionEnd)
  return ThisRegionFullline

#---------------------------------------------------------------
# Reference (no longer used)
# class ExpandSelectionToSentenceCommand(sublime_plugin.TextCommand):
#   def run(self, edit):
#     view = self.view
#     oldSelRegions = list(view.sel())
#     view.sel().clear()
#     for ThisRegion in oldSelRegions:
#       ThisRegionBeg = ThisRegion.begin() - 1
#       while( (view.substr(ThisRegionBeg) not in ".") and (ThisRegionBeg >= 0)):
#         ThisRegionBeg -= 1

#       ThisRegionBeg += 1
#       while( (view.substr(ThisRegionBeg) in whitespaceChars) and (ThisRegionBeg < view.size())):
#         ThisRegionBeg += 1

#       ThisRegionEnd = ThisRegion.end()
#       while( (view.substr(ThisRegionEnd) not in ".") and (ThisRegionEnd < view.size())):
#         ThisRegionEnd += 1

#       if(ThisRegionBeg != ThisRegionEnd):
#         view.sel().add(sublime.Region(ThisRegionBeg, ThisRegionEnd+1))
#       else:
#         view.sel().add(sublime.Region(ThisRegionBeg, ThisRegionBeg))

#---------------------------------------------------------------
# Reference (no longer used)
# class MoveToContigboundaryCommand(sublime_plugin.TextCommand):
#   def run(self, edit, forward, extend=False):
#     view = self.view
#     oldSelRegions = list(view.sel())
#     view.sel().clear()
#     for ThisRegion in oldSelRegions:
#       if(forward): #forward
#         caretPos = ThisRegion.b
#         if(view.substr(caretPos) in whitespaceChars): #initially have whitespace right of me, find char
#           while( (view.substr(caretPos) in whitespaceChars) and (caretPos < view.size())):
#             caretPos += 1
#         else: #initially have char right of me, find whitespace
#           while( (view.substr(caretPos) not in whitespaceChars) and (caretPos < view.size())):
#             caretPos += 1
#         if(extend):
#           view.sel().add(sublime.Region(ThisRegion.a, caretPos))
#           view.show(caretPos)
#         else:
#           view.sel().add(sublime.Region(caretPos))
#           view.show(caretPos)
#       else: #backward
#         caretPos = ThisRegion.b - 1
#         if(view.substr(caretPos) in whitespaceChars): #initially have whitespace left of me, find char
#           while( (view.substr(caretPos) in whitespaceChars) and (caretPos >= 0)):
#             caretPos -= 1
#         else: #initially have char left of me, find whitespace
#           while( (view.substr(caretPos) not in whitespaceChars) and (caretPos >= 0)):
#             caretPos -= 1
#         if(extend):
#           view.sel().add(sublime.Region(ThisRegion.a, caretPos+1))
#           view.show(caretPos+1)
#         else:
#           view.sel().add(sublime.Region(caretPos+1))
#           view.show(caretPos+1)

#---------------------------------------------------------------
