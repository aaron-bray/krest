/* This file is part of SEAL-TK, and is distributed under the OSI-approved BSD
 * 3-Clause License. See top-level LICENSE file or
 * https://github.com/Kitware/seal-tk/blob/master/LICENSE for details. */

#ifndef sealtk_core_VideoSource_hpp
#define sealtk_core_VideoSource_hpp

#include <QImage>
#include <QObject>
#include <qtGlobal.h>

#include <vital/types/timestamp.h>

#include <set>

namespace sealtk
{

namespace core
{

class VideoSourcePrivate;

class VideoSource : public QObject
{
  Q_OBJECT

public:
  explicit VideoSource(QObject* parent = nullptr);
  ~VideoSource() override;

  virtual std::set<kwiver::vital::timestamp::time_t> times() const = 0;

signals:
  void imageDisplayed(QImage const& image);
  void videoInputChanged();

public slots:
  virtual void seek(kwiver::vital::timestamp::time_t time) = 0;

protected:
  QTE_DECLARE_PRIVATE(VideoSource)

private:
  QTE_DECLARE_PRIVATE_RPTR(VideoSource)
};

}

}

#endif
