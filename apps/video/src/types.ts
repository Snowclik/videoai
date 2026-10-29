export interface WordTimestamp {
  word: string;
  start_sec: number;
  end_sec: number;
  start_frame: number;
  end_frame: number;
}

export interface ClipData {
  id: string;
  title: string;
  tag: string;
  accent_color: string;
  video_source: string;
  clean_audio: string;
  source_start_sec: number;
  source_end_sec: number;
  source_start_frame: number;
  duration_sec: number;
  duration_frames: number;
  global_start_frame: number;
  global_end_frame: number;
  full_text: string;
  words: WordTimestamp[];
  has_zoom: boolean;
  is_theme_transition?: boolean;
}

export interface TimelineData {
  version: string;
  settings: {
    fps: number;
    width: number;
    height: number;
    orientation: string;
    background_music: string;
    music_volume: number;
    transition_sfx: string;
  };
  total_duration_sec: number;
  total_frames: number;
  clips: ClipData[];
}
