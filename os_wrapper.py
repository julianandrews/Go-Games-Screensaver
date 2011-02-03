# Copyright (c) 2010 Julian Andrews.
# All rights reserved.
#
# This software is provided for personal use only, and may not be 
# redistributed in whole or in part or used for any comercial purpose without
# the permision of the copyright holder.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
# JULIAN ANDREWS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# I will probably release this with a more permissive license at some later
# date, but for the moment want to keep my options open until I decide how
# best to distribute it.

import platform

s = platform.system()

if s == 'Windows':
    from scr_windows import get_mode, WinSSWindow as SSWindow
    data_folder = "E:\\julian\\coding\\gogames-screensaver\\data"
elif s == 'Linux':
    from scr_linux import GsThemeWindow as SSWindow
    data_folder = "/usr/share/gogames-screensaver"
    def get_mode():
        return None, None
else:
    raise RuntimeError("Unsuported OS: %s" % s)
